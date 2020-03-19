# gl.py - Functions to simplify the GL interfaces.

from    ctypes          import c_void_p, sizeof
import  glm
from    OpenGL.GL       import *
import  PIL.Image
import  types
import  warnings

# Set up the initial OpenGL state.
def init ():
    # Basics
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_CULL_FACE)
    glPointSize(5)

    # Lighting (XXX should be in the world)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHT0)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    # blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # pixel transfer
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    # textures
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

# Clear the buffers
def clear ():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def make_normal_matrix (model):
    return glm.transpose(glm.inverse(glm.mat3(model)))

# Used by Texture below.
_tex_wrap = {
    False:      GL_CLAMP,
    True:       GL_REPEAT,
    "clamp":    GL_CLAMP,
    "repeat":   GL_REPEAT,
    "border":   GL_CLAMP_TO_BORDER,
    "edge":     GL_CLAMP_TO_EDGE,
}
_tex_filter = {
    "nearest":  GL_NEAREST,
    "linear":   GL_LINEAR,
    "mipmapNN": GL_NEAREST_MIPMAP_NEAREST,
    "mipmapLN": GL_LINEAR_MIPMAP_NEAREST,
    "mipmapNL": GL_NEAREST_MIPMAP_LINEAR,
    "mipmapLL": GL_LINEAR_MIPMAP_LINEAR,
    "mipmap":   GL_LINEAR_MIPMAP_LINEAR,
    False:      GL_NEAREST,
    True:       GL_LINEAR_MIPMAP_LINEAR,
}
_tex_mipmaps = {
    GL_NEAREST:                 (GL_NEAREST, False),
    GL_LINEAR:                  (GL_LINEAR, False),
    GL_NEAREST_MIPMAP_NEAREST:  (GL_NEAREST, True),
    GL_NEAREST_MIPMAP_LINEAR:   (GL_LINEAR, True),
    GL_LINEAR_MIPMAP_NEAREST:   (GL_NEAREST, True),
    GL_LINEAR_MIPMAP_LINEAR:    (GL_LINEAR, True),
}

# This object represents a GL texture
class Texture:
    __slots__ = [
        "id",       # Our texture ID
        "target",   # Our texture target
        "mipmaps",  # Do we want mipmaps?
    ]

    # Create a new texture. Accepts keyword arguments:
    #   target                  Defaults to GL_TEXTURE_2D
    #   filter  as above        Linear or nearest filtering
    #   clamp   as above        Texture wrapping behaviour
    # Leaves the new texture bound, and returns the ID.
    def __init__ (self, **kwargs):
        self.id = glGenTextures(1)

        self.target = GL_TEXTURE_2D
        if "target" in kwargs:
            self.target = kwargs["target"]

        if "filter" in kwargs:
            self.set_filter(kwargs["filter"])
        else:
            self.set_filter(True)

        if "wrap" in kwargs:
            self.set_wrap(kwargs["wrap"])

    def delete (self):
        glDeleteTextures(1, [self.id])

    def set_filter (self, filt):
        if isinstance(filt, tuple):
            minf        = _tex_filter[filt[0]]
            magf        = _tex_filter[filt[1]]
            mip         = _tex_mipmaps[minf][1]
        else:
            minf        = _tex_filter[filt]
            (magf, mip) = _tex_mipmaps[minf]

        self.bind()
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, minf)
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, magf)

        self.mipmaps    = mip

    def set_wrap (self, to):
        wrap = _tex_wrap[to]
        self.bind()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)

    def bind (self):
        glBindTexture(self.target, self.id)

    def enable (self):
        glEnable(self.target)

    def disable (self):
        glDisable(self.target)

    def use (self):
        self.bind()
        self.enable()

    # Load an image into a texture.
    def load (self, fmt, w, h, array):
        self.bind()
        glTexImage2D(self.target, 0, fmt, w, h, 0, fmt, GL_UNSIGNED_BYTE,
            array)
        if self.mipmaps:
            glGenerateMipmap(self.target)

    def load_file (self, fmt, f):
        img = PIL.Image.open(f)
        img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.load(fmt, img.width, img.height, img.tobytes())

# Shader programs

_shader_types = {
    "vertex":   GL_VERTEX_SHADER,
    "fragment": GL_FRAGMENT_SHADER,
}

class ShaderProg:
    __slots__   = ["id"]

    def __init__ (self, prg):
        self.id = prg

    def use (self):
        glUseProgram(self.id)

    def delete (self):
        glDeleteProgram(self.id)

class ShaderCompiler:
    __slots__ = ["objs"]

    def __init__ (self):
        self.objs   = {}

    def delete (self):
        for i in self.objs:
            glDeleteShader(self.objs[i])

    def compile_str (self, typ, name, src):
        sh = glCreateShader(_shader_types[typ])
        glShaderSource(sh, src)
        glCompileShader(sh)

        if not glGetShaderiv(sh, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(sh)
            raise RuntimeError("Shader compilation failed: " + log.decode())

        self.objs[name] = sh
        return sh

    def compile_file (self, typ, name, fname):
        # XXX search path etc.
        with open(fname, "rb") as f:
            src = f.read()
        return self.compile_str(typ, name, src)

    def find_shader (self, typ, name):
        if name in self.objs:
            return self.objs[name]
        return self.compile_file(typ, name, "glsl/" + name + ".glsl")

    def link (self, shs):
        prg = glCreateProgram()
        for sh in shs:
            glAttachShader(prg, sh)

        glLinkProgram(prg)

        if not glGetProgramiv(prg, GL_LINK_STATUS):
            log = glGetProgramInfoLog(prg)
            raise RuntimeError("Shader link failed: " + log.decode())

        return prg

    def _build_att_method (self, ns, prg, i):
        info    = glGetActiveAttrib(prg, i)
        att     = info[0].decode()
        if att[0:3] == "gl_":
            return

        loc     = glGetAttribLocation(prg, att)
        if loc == -1:
            warnings.warn("Could not find attrib location for " + att)
            return

        ns[att] = loc

        print("Added attrib", att)

    def _find_uni_loc (self, prg, att):
        loc     = glGetUniformLocation(prg, att)
        if loc == -1:
            warnings.warn("Could not find uniform location for " + att)
            return
        return loc

    def _build_uni_method (self, ns, prg, i):
        info    = glGetActiveUniform(prg, i)
        att     = info[0].decode()
        if att[0:3] == "gl_":
            return

        typ     = info[2]

        meth    = att.replace(".", "_")
        meth    = meth.replace("[", "").replace("]", "")

        if info[1] == 1:
            self._build_uni_lambda(ns, meth, prg, att, typ)
        else:
            att     = att[0:-3]
            meth    = meth[0:-1]
            for i in range(info[1]):
                self._build_uni_lambda(ns, meth + str(i),
                    prg, att + "[" + str(i) + "]", typ)

    def _build_uni_lambda (self, ns, meth, prg, att, typ):
        loc     = glGetUniformLocation(prg, att)
        typn    = None

        if typ == GL_FLOAT:
            ns[meth] = lambda s, v: glUniform1f(loc, v)
            typn = "float"
        elif typ == GL_FLOAT_VEC3:
            ns[meth] = lambda s, v: glUniform3fv(loc, 1, glm.value_ptr(v))
            typn = "vec3"
        elif typ == GL_FLOAT_VEC4:
            ns[meth] = lambda s, v: glUniform4fv(loc, 1, glm.value_ptr(v))
            typn = "vec4"
        elif typ == GL_SAMPLER_2D:
            ns[meth] = lambda s, v: glUniform1i(loc, v)
            typn = "sampler2D"
        elif typ == GL_FLOAT_MAT3:
            ns[meth] = lambda s, v: \
                glUniformMatrix3fv(loc, 1, GL_FALSE, glm.value_ptr(v))
            typn = "mat3"
        elif typ == GL_FLOAT_MAT4:
            ns[meth] = lambda s, v: \
                glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(v))
            typn = "mat4"
        else:
            raise RuntimeError("Unhandled uniform" + att)

        print("Added uniform", typn, att, "as", meth)

    def _build_shader_class (self, ns, prg):
        n_att   = glGetProgramiv(prg, GL_ACTIVE_ATTRIBUTES)
        n_uni   = glGetProgramiv(prg, GL_ACTIVE_UNIFORMS)

        for i in range(n_att):
            self._build_att_method(ns, prg, i)
        for i in range(n_uni):
            self._build_uni_method(ns, prg, i)

    def build_shader_obj (self, prg):
        C = types.new_class("ShaderProgX", 
            bases=(ShaderProg,),
            exec_body=lambda ns: self._build_shader_class(ns, prg))
        return C(prg)

    def build_shader (self, vxs, frs):
        objs    = [self.find_shader("vertex", i) for i in vxs]
        objs    += [self.find_shader("fragment", i) for i in frs]
        prg     = self.link(objs)
        print("Building for", vxs, frs)
        return self.build_shader_obj(prg)

class Shader:
    __slots__ = ["id", "objs", "attribs", "uniforms"]

    def __init__ (self):
        self.id     = glCreateProgram()
        self._clear()

    def _clear (self):
        self.objs       = []
        self.attribs    = {}
        self.uniforms   = {}

    def add_shader (self, typ, src):
        sh = glCreateShader(_shader_types[typ])
        glShaderSource(sh, src)
        glCompileShader(sh)

        if not glGetShaderiv(sh, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(sh)
            raise RuntimeError("Shader compilation failed: " + log.decode())

        glAttachShader(self.id, sh)
        self.objs.append(sh)

    def link (self):
        glLinkProgram(self.id)

        if not glGetProgramiv(self.id, GL_LINK_STATUS):
            log = glGetProgramInfoLog(self.id)
            raise RuntimeError("Shader link failed: " + log.decode())

        for o in self.objs:
            glDeleteShader(o)

        self._clear()

    def use (self):
        glUseProgram(self.id)

    def _cached (self, cache, att, lookup):
        if att in cache:
            return cache[att]

        loc = lookup(self.id, att)
        if loc < 0:
            raise RuntimeError("Unknown attrib/uniform " + att)
        cache[att] = loc
        return loc

    def get_attrib (self, att):
        return self._cached(self.attribs, att, glGetAttribLocation)

    def _get_uniform_loc (self, name):
        return self._cached(self.uniforms, name, glGetUniformLocation)

    def set_uniform4f (self, name, a, b, c, d):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniform4f(loc, a, b, c, d)

    def set_uniform4v (self, name, value):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniform4fv(loc, 1, glm.value_ptr(value))

    def set_uniform3f (self, name, a, b, c):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniform3f(loc, a, b, c)

    def set_uniform3v (self, name, value):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniform3fv(loc, 1, glm.value_ptr(value))

    def set_uniform1f (self, name, value):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniform1f(loc, value)

    def set_uniform1i (self, name, value):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniform1i(loc, value)

    def set_matrix3 (self, name, mat):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniformMatrix3fv(loc, 1, GL_FALSE, glm.value_ptr(mat))

    def set_matrix4 (self, name, mat):
        loc = self._get_uniform_loc(name)
        self.use()
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(mat))

# VBOs

_buftypes = {
    "vbo":  GL_ARRAY_BUFFER,
    "ebo":  GL_ELEMENT_ARRAY_BUFFER,
}

class Buffer:
    __slots__ = ["targ", "id", "usage"]

    def __init__ (self, typ, data=None):
        self.targ   = _buftypes[typ]
        self.id     = glGenBuffers(1)

        print("Created", typ, "buffer", self.id)

        if data is not None:
            self.load(data)

    def delete (self):
        print("Deleting buffer", self.id)
        glDeleteBuffers(1, [self.id])

    def bind (self):
        glBindBuffer(self.targ, self.id)

    def unbind (self):
        glBindBuffer(self.targ, 0)

    def load (self, data):
        self.bind()
        glBufferData(self.targ, data, GL_STATIC_DRAW)

# VAOs

class VAO:
    __slots__ = [
        "id",           # our VAO id
        "shader",       # Our shader program
        "ebo",          # our EBO (a Buffer)
        "primitives",   # the list of primitives we render
        "textures",     # textures to bind before we render
    ]

    def __init__ (self, shader=None):
        self.id         = glGenVertexArrays(1)
        self.shader     = shader
        self.ebo        = None
        self.primitives = []
        self.textures   = []

        print("Created VAO", self.id)

    def delete (self):
        print("Deleting VAO", self.id)
        glDeleteVertexArrays(1, [self.id])
        if self.ebo is not None:
            self.ebo.delete()

    def bind (self):
        glBindVertexArray(self.id)

    def unbind (self):
        glBindVertexArray(0)
        if self.ebo is not None:
            self.ebo.unbind()

    def setup_attrib (self, att, length, stride, offset):
        ix  = self.shader.get_attrib(att)
        self.bind()
        self.add_attrib(ix, length, stride, offset)

    def add_attrib (self, ix, length, stride, offset):
        sz = sizeof(GLfloat)
        glVertexAttribPointer(ix, length, GL_FLOAT, GL_FALSE,
            stride*sz, c_void_p(offset*sz))
        glEnableVertexAttribArray(ix)
        #print("VAO", self.id, "attrib", ix, length, stride, offset)

    def add_ebo (self, ebo):
        self.ebo    = ebo
        self.bind()
        ebo.bind()

    def add_primitive (self, mode, off, n):
        self.primitives.append((mode, off, n))

    def set_texture (self, n, tex):
        self.textures[n] = tex

    def add_texture (self, tex):
        n = len(self.textures)
        self.textures.append(tex)
        return n

    def set_matrix3 (self, name, matrix):
        self.shader.set_matrix3(name, matrix)

    def set_matrix4 (self, name, matrix):
        self.shader.set_matrix4(name, matrix)

    def use (self):
        for i in range(len(self.textures)):
            glActiveTexture(GL_TEXTURE0 + i)
            self.textures[i].bind()

        if self.shader is not None:
            self.shader.use()
        self.bind()

    def render (self):
        for p in self.primitives:
            (mode, off, n) = p
            if self.ebo is None:
                glDrawArrays(mode, off, n)
            else:
                glDrawElements(mode, n, GL_UNSIGNED_INT, c_void_p(off))


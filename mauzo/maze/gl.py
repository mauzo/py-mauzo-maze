# gl.py - Functions to simplify the GL interfaces.

from    ctypes          import c_void_p, sizeof
import  glm
from    OpenGL.GL       import *
import  numpy           as np
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

# Revert to the GL1 fixed-function pipeline
def use_ffp ():
    glUseProgram(0)

# Load a matrix into the FFP.
def load_ffp_matrix (mat):
    # Push the matrix to GL (I don't understand why value_ptr
    # doesn't work here when it does with glUniformMatrix...)
    ary  = np.ndarray((4, 4), buffer=mat, dtype=np.float32)
    glLoadMatrixf(ary)

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
_tex_format = {
    "RGBA":     GL_RGBA,
    "RGB":      GL_RGB,
    "L":        GL_ALPHA,
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

        if "file" in kwargs:
            self.load_file(kwargs["file"])

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
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, wrap)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, wrap)

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

    def load_file (self, f):
        img = PIL.Image.open(f)
        img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        fmt = _tex_format[img.mode]
        self.load(fmt, img.width, img.height, img.tobytes())

# Shader programs

class ShaderProg:
    # No __slots__, so we can add methods as needed

    def __init__ (self, prg):
        self.id         = prg
        self._next_tex  = 0

        self.use()
        self.__init_glsl_methods()

    def use (self):
        glUseProgram(self.id)

    def delete (self):
        glDeleteProgram(self.id)

    def __init_glsl_methods (self):
        prg     = self.id
        n_att   = glGetProgramiv(prg, GL_ACTIVE_ATTRIBUTES)
        n_uni   = glGetProgramiv(prg, GL_ACTIVE_UNIFORMS)

        for i in range(n_att):
            self.__init_attrib(i)
        for i in range(n_uni):
            self.__init_uniform(i)

    def __init_attrib (self, i):
        prg     = self.id
        info    = glGetActiveAttrib(prg, i)
        att     = info[0].decode()
        if att[0:3] == "gl_":
            return

        loc     = glGetAttribLocation(prg, att)
        if loc == -1:
            warnings.warn("Could not find attrib location for " + att)
            return

        self.__dict__[att] = loc

        print("Added attrib", att)

    def __init_uniform (self, i):
        info    = glGetActiveUniform(self.id, i)
        att     = info[0].decode()
        if att[0:3] == "gl_":
            return

        typ     = info[2]
        meth    = att.replace(".", "_")
        meth    = meth.replace("[", "").replace("]", "")

        if info[1] == 1:
            (typn, fn) = self._build_uni_lambda(att, typ)
            self.__dict__[meth] = fn
            print("Added uniform", typn, att, "as", meth)
        else:
            att     = att[0:-3]
            meth    = meth[0:-1]
            for i in range(info[1]):
                m = "%s%u" % (meth, i)
                a = "%s[%u]" % (att, i)
                (typn, fn) = self._build_uni_lambda(a, typ)
                self.__dict__[m] = fn
                print("Added uniform", typn, a, "as", meth)

    def _build_uni_lambda (self, att, typ):
        loc     = glGetUniformLocation(self.id, att)

        if typ == GL_FLOAT:
            return "float", lambda v: glUniform1f(loc, v)
        elif typ == GL_FLOAT_VEC3:
            return "vec3", lambda v: glUniform3fv(loc, 1, glm.value_ptr(v))
        elif typ == GL_FLOAT_VEC4:
            return "vec4", lambda v: glUniform4fv(loc, 1, glm.value_ptr(v))
        elif typ == GL_FLOAT_MAT3:
            return "mat3", lambda v: \
                glUniformMatrix3fv(loc, 1, GL_FALSE, glm.value_ptr(v))
        elif typ == GL_FLOAT_MAT4:
            return "mat4", lambda v: \
                glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(v))
        elif typ == GL_SAMPLER_2D:
            # For textures we allocate a texture unit and set it
            # immediately. Then the method binds a texture to the
            # appropriate unit.
            u = self._next_tex
            self._next_tex += 1
            glUniform1i(loc, u)
            def bind_tex (t):
                glActiveTexture(GL_TEXTURE0 + u)
                # We don't need to t.use (which calls glEnable) as that
                # only applies to FF rendering.
                t.bind()
            return "sampler2D", bind_tex
        else:
            raise RuntimeError("Unhandled uniform" + att)

_shader_types = {
    "vert": GL_VERTEX_SHADER,
    "frag": GL_FRAGMENT_SHADER,
}

class ShaderCompiler:
    __slots__ = ["objs"]

    def __init__ (self):
        self.objs   = {}

    def delete (self):
        for i in self.objs:
            glDeleteShader(self.objs[i])

    def compile_str (self, typ, src):
        sh = glCreateShader(typ)
        glShaderSource(sh, src)
        glCompileShader(sh)

        if not glGetShaderiv(sh, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(sh)
            raise RuntimeError("Shader compilation failed: " + log.decode())

        return sh

    def compile_file (self, typ, name):
        with open(name, "rb") as f:
            src = f.read()
        return self.compile_str(typ, src)

    def find_shader (self, typ, name):
        gltyp   = _shader_types[typ]
        name    = "glsl/%s.%s" % (name, typ)

        if name in self.objs:
            return self.objs[name]

        sh      = self.compile_file(gltyp, name)
        self.objs[name] = sh
        return sh

    def link (self, shs):
        prg = glCreateProgram()
        for sh in shs:
            glAttachShader(prg, sh)

        glLinkProgram(prg)

        if not glGetProgramiv(prg, GL_LINK_STATUS):
            log = glGetProgramInfoLog(prg)
            raise RuntimeError("Shader link failed: " + log.decode())

        return prg

    def build_shader (self, **kwargs):
        print("Building for", kwargs)
        objs    = [
            self.find_shader(t, kwargs[t])
                for t in kwargs]
        prg     = self.link(objs)
        return ShaderProg(prg)

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
    ]

    def __init__ (self, shader=None):
        self.id         = glGenVertexArrays(1)
        self.shader     = shader
        self.ebo        = None
        self.primitives = []

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

    def use (self):
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


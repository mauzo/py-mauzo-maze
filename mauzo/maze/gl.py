# gl.py - Functions to simplify the GL interfaces.

from    ctypes          import c_void_p, sizeof
import  glm
from    OpenGL.GL       import *
import  PIL.Image

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

# Used by Texture below.
_tex_wrap = {
    False:      GL_CLAMP,
    True:       GL_REPEAT,
    "clamp":    GL_CLAMP,
    "repeat":   GL_REPEAT,
    "border":   GL_CLAMP_TO_BORDER,
    "edge":     GL_CLAMP_TO_EDGE,
}

# This object represents a GL texture
class Texture:
    __slots__ = [
        # Our texture ID
        "id",
        # Our texture target
        "target",
    ]

    # Create a new texture. Accepts keyword arguments:
    #   target                  Defaults to GL_TEXTURE_2D
    #   linear  True|False      Linear or nearest filtering
    #   clamp   as above        Texture wrapping behaviour
    # Leaves the new texture bound, and returns the ID.
    def __init__ (self, **kwargs):
        self.id = glGenTextures(1)

        self.target = GL_TEXTURE_2D
        if "target" in kwargs:
            self.target = kwargs["target"]

        if "linear" in kwargs:
            self.set_linear(kwargs["linear"])
        else:
            self.set_linear(True)

        if "wrap" in kwargs:
            self.set_wrap(kwargs["wrap"])

    def delete (self):
        glDeleteTextures(1, [self.id])

    def set_linear (self, lin):
        filt = (GL_LINEAR if lin else GL_NEAREST)
        self.bind()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filt)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filt)

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

    # Load an image into a texture.
    def load (self, fmt, w, h, array):
        self.bind()
        glTexImage2D(self.target, 0, fmt, w, h, 0, fmt, GL_UNSIGNED_BYTE,
            array)

    def load_file (self, fmt, f):
        img = PIL.Image.open(f)
        img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.load(fmt, img.width, img.height, img.tobytes())

# Shader programs

_shader_types = {
    "vertex":   GL_VERTEX_SHADER,
    "fragment": GL_FRAGMENT_SHADER,
}

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
            log = glGetShaderInfoLog(self.id)
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

    def _set_uniform (self, name, setter, value):
        loc = self._get_uniform_loc(name)
        self.use()
        setter(loc, value)

    def set_uniform4f (self, name, value):
        self._set_uniform(name, glUniform4fv, value)

    def set_uniform3f (self, name, value):
        self._set_uniform(name, glUniform3fv, value)

    def set_uniform1f (self, name, value):
        self._set_uniform(name, glUniform1f, value)

    def set_uniform1i (self, name, value):
        self._set_uniform(name, glUniform1i, value)

    def set_uniform_matrix4 (self, name, mat):
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
        "shader",       # our shader (a Shader)
        "vbo",          # our VBO (a Buffer)
        "ebo",          # our EBO (a Buffer)
        "primitives",   # the list of primitives we render
        "textures",     # textures to bind before we render
    ]

    def __init__ (self, shader):
        self.id         = glGenVertexArrays(1)
        self.shader     = shader
        self.vbo        = None
        self.ebo        = None
        self.primitives = []
        self.textures   = []

        print("Created VAO", self.id)

    def delete (self):
        print("Deleting VAO", self.id)
        glDeleteVertexArrays(1, [self.id])
        if self.vbo is not None:
            self.vbo.delete()
        if self.ebo is not None:
            self.ebo.delete()

    def bind (self):
        glBindVertexArray(self.id)

    def unbind (self):
        glBindVertexArray(0)
        if self.vbo is not None:
            self.vbo.unbind()
        if self.ebo is not None:
            self.ebo.unbind()

    def add_vbo (self, vbo):
        self.vbo    = vbo

    def setup_attrib (self, att, length, stride, offset):
        ix = self.shader.get_attrib(att)

        self.bind()
        self.vbo.bind()

        sz = sizeof(GLfloat)
        glVertexAttribPointer(ix, length, GL_FLOAT, GL_FALSE,
            stride*sz, c_void_p(offset*sz))
        glEnableVertexAttribArray(ix)

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

    def use (self):
        for i in range(len(self.textures)):
            glActiveTexture(GL_TEXTURE0 + i)
            self.textures[i].bind()

        self.shader.use()
        self.bind()

    def render (self):
        for p in self.primitives:
            (mode, off, n) = p
            if self.ebo is None:
                glDrawArrays(mode, off, n)
            else:
                glDrawElements(mode, n, GL_UNSIGNED_INT, c_void_p(off))


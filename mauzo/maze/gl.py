# gl.py - Functions to simplify the GL interfaces.

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


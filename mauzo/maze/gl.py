# gl.py - Functions to simplify the GL interfaces.

from    OpenGL.GL       import *

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

# Used by new_texture below.
_tex_clamp = {
    True:       GL_CLAMP,
    False:      GL_REPEAT,
    "border":   GL_CLAMP_TO_BORDER,
    "edge":     GL_CLAMP_TO_EDGE,
}

# Create a new texture. Accepts keyword arguments:
#   linear  True|False      Linear or nearest filtering
#   clamp   as above        Texture wrapping behaviour
# Leaves the new texture bound, and returns the ID.
def new_texture (**kwargs):
    tex = glGenTextures(1)

    filt    = GL_LINEAR
    if "linear" in kwargs:
        filt = (GL_LINEAR if kwargs["linear"] else GL_NEAREST)

    wrap    = GL_REPEAT
    if "clamp" in kwargs:
        wrap = _tex_clamp[kwargs["clamp"]]

    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filt)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filt)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap)
    return tex

# Load an image into a texture. The texture must already be bound.
def load_texture (fmt, w, h, array):
    glTexImage2D(GL_TEXTURE_2D, 0, fmt, w, h, 0, fmt, GL_UNSIGNED_BYTE,
        array)


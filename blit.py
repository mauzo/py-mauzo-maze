import  numpy               as np
from    OpenGL.GL           import *
import  pygame
from    pygame.locals       import *
import  pygame.freetype
import  signal

def sigint (x, y):
    raise KeyboardInterrupt()

def eloop ():
    pygame.event.get()

def flip ():
    pygame.display.flip()

def clear ():
    glClear(GL_COLOR_BUFFER_BIT)
    flip()
    glClear(GL_COLOR_BUFFER_BIT)
    flip()

WINSIZE = (0, 400, 0, 100)

def init_display ():
    pygame.display.init()
    pygame.freetype.init()

    signal.signal(signal.SIGINT, sigint)

    size = (WINSIZE[1] - WINSIZE[0], WINSIZE[3] - WINSIZE[2])
    pygame.display.set_mode(size, OPENGL|DOUBLEBUF)
    eloop()

def init_gl ():
    # colours
    glClearColor(0, 0, 0, 1)
    glColor(1, 0, 1, 1)

    # blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    glPointSize(5)

    # pixel transfer
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    # textures
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

    # projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(*WINSIZE, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def square (l, t, r, b):
    glBegin(GL_TRIANGLE_FAN)
    glTexCoord2f(l, t)
    glVertex2f(-50, 50)
    glTexCoord2f(l, b)
    glVertex2f(-50, -50)
    glTexCoord2f(r, b)
    glVertex2f(50, -50)
    glTexCoord2f(r, t)
    glVertex2f(50, 50)
    glEnd()

_tex_clamp = {
    True:       GL_CLAMP,
    False:      GL_REPEAT,
    "border":   GL_CLAMP_TO_BORDER,
    "edge":     GL_CLAMP_TO_EDGE,
}

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

def load_texture (fmt, w, h, array):
    glTexImage2D(GL_TEXTURE_2D, 0, fmt, w, h, 0, fmt, GL_UNSIGNED_BYTE,
        array)

class Glyph:
    __slots__ = ["texture", "metrics"]

    def __init__ (self, font, char):
        self.metrics    = font.get_metrics(char)[0]
        (buf, size)     = font.render_raw(char)

        if size == (0, 0):
            self.texture = None
        else:
            self.texture = new_texture(clamp=True, linear=True)
            load_texture(GL_ALPHA, *size, buf)

    def advance (self, x, y):
        m = self.metrics
        return (x + m[4], y + m[5])

    def show (self, x, y):
        m = self.metrics

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0, 0)
        glVertex2f(x + m[0], y + m[3])
        glTexCoord2f(0, 1)
        glVertex2f(x + m[0], y + m[2])
        glTexCoord2f(1, 1)
        glVertex2f(x + m[1], y + m[2])
        glTexCoord2f(1, 0)
        glVertex2f(x + m[1], y + m[3])
        glEnd()
        glDisable(GL_TEXTURE_2D)

        return (x + m[4], y + m[5])

class GLFont:
    __slots__ = ["height", "characters"]

    def __init__ (self, font_name, height):
        # XXX We probably don't want to use system fonts.
        font    = pygame.freetype.SysFont(font_name, height)
        
        chars = {}
        # XXX This is the usable range of ASCII, which will do for now.
        for i in range(32, 127):
            c = chr(i)
            chars[c] = Glyph(font, c)

        self.height     = height
        self.characters = chars

    def advance (self, msg):
        chars   = self.characters
        (x, y)  = (0, 0)

        for c in msg:
            (x, y) = chars[c].advance(x, y)

        return (x, y)

    def show (self, msg, x, y):
        chars   = self.characters

        for c in msg:
            (x, y) = chars[c].show(x, y)

        return (x, y)

init_display()
init_gl()

yellow_px       = b'\xee\xdd\x00'
yellow_16x16    = yellow_px * 16*16
yellow_tex      = new_texture()
load_texture(GL_RGB, 16, 16, yellow_16x16)

stencil         = GLFont("Stencil", 100)

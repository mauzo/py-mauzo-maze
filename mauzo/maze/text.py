# text.py - functions for drawing text.

from    OpenGL.GL       import *
import  pygame.freetype

from    .       import display
from    .       import gl

def init ():
    pygame.freetype.init()

# Push new GL state suitable for rendering text.
def push_gl_state ():
    (w, h) = display.Display["viewport"]

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glPushAttrib(GL_ENABLE_BIT|GL_TEXTURE_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND)

# Pop the state pushed above.
def pop_gl_state ():
    glPopAttrib()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

class Glyph:
    __slots__ = ["texture", "metrics"]

    def __init__ (self, font, char):
        self.metrics    = font.get_metrics(char)[0]
        (buf, size)     = font.render_raw(char)

        if size == (0, 0):
            self.texture = None
        else:
            self.texture = gl.new_texture(clamp=True, linear=True)
            gl.load_texture(GL_ALPHA, *size, buf)

    def advance (self, x, y):
        m = self.metrics
        return (x + m[4], y + m[5])

    def show (self, x, y):
        m = self.metrics

        if self.texture:
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


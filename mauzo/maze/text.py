# text.py - functions for drawing text.

from    OpenGL.GL       import *
import  pygame.freetype

from    .       import gl

TWO16   = 2**16
TWO32   = 2**32

def init ():
    pygame.freetype.init()

class Glyph:
    __slots__ = ["texture", "metrics"]

    def __init__ (self, font, char):
        metrics         = font.get_metrics(char)[0]
        (buf, size)     = font.render_raw(char)

        self.metrics = tuple(
            x - TWO32 if x > TWO16 else x
                for x in metrics)

        if size == (0, 0):
            self.texture = None
        else:
            tex = gl.Texture(wrap="clamp", filter="linear")
            tex.load(GL_ALPHA, *size, buf)
            self.texture = tex

    def advance (self, x, y):
        m = self.metrics
        return (x + m[4], y + m[5])

    def show (self, x, y):
        m = self.metrics

        if self.texture:
            tex = self.texture
            tex.bind()
            tex.enable()
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
            tex.disable()

        return (x + m[4], y + m[5])

class GLFont:
    __slots__ = ["height", "characters"]

    def __init__ (self, font_name, height):
        ffile   = "font/" + font_name
        font    = pygame.freetype.Font(ffile, height)
        
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

    def show (self, msg, x, y, size):
        chars   = self.characters
        size    = size/self.height

        glPushMatrix()
        glTranslate(x, y, 0)
        glScale(size, size, size)

        (x, y) = (0, 0)
        for c in msg:
            (x, y) = chars[c].show(x, y)

        glPopMatrix()

        return (x, y)


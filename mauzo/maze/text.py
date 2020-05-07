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

    def show3 (self, ctx):
        m       = self.metrics

        if self.texture:
            (x, y)  = (ctx.x, ctx.y)
            pen     = ctx.pen

            pen.update_buf(x + m[0], y + m[2], x + m[1], y + m[3])
            pen.set_texture(self.texture)
            pen.render()

        ctx.x   += m[4]
        ctx.y   += m[5]

class Pen:
    __slots__ = [
        "vao",
        "vbo",
        "shader",
    ]

    def __init__ (self, slc):
        prg     = slc.build_shader(vert="plain", frag="text")
        vao     = gl.VAO()
        vbo     = gl.Buffer("vbo")

        buf     = gl.make_buffer([
            # vertices: to be updated
            0, 0, 0,    0, 0, 0,    0, 0, 0,    0, 0, 0,
            # tex coords: static
            0, 0,       0, 1,       1, 1,       1, 0,
        ])

        vbo.bind()
        vbo.load(buf, GL_STREAM_DRAW)

        vao.bind()
        vao.add_attrib(prg.b_pos, 3, 3, 0)
        vao.add_attrib(prg.b_tex, 2, 2, 12)
        (x, y)  = (ctx.x, ctx.y)
        pen     = ctx.pen

        pen.update_buf(x + m[0], y + m[2], x + m[1], y + m[3])
        pen.set_texture(self.texture)
        pen.render()
        vao.add_primitive(GL_QUADS, 0, 4)
        vao.unbind()
        vbo.unbind()

        self.vao    = vao
        self.vbo    = vbo
        self.shader = prg

    def use (self):
        self.shader.use()
        self.vao.use()

    def set_origin_scale (self, x, y, scale):
        model   = glm.translate(mat4(1), vec3(x, y, 0))
        model   = glm.scale(model, vec3(scale))
        self.shader.u_model(model)

    def set_texture (self, tex):
        self.shader.u_char_texture(tex)

    def update_buf (self, x0, y0, x1, y1):
        buf     = gl.make_buffer([
            x0, y1, 0,  x0, y0, 0,  x1, y0, 0,  x1, y1, 0,
        ])
        self.vbo.update(0, buf)

    def render (self):
        self.vao.render()

class TextContext:
    __slots__ = [
        "x", "y",   # our current position
        "pen",      # a Pen to draw with
    ]

    def __init__ (self, pen):
        self.pen    = pen
        self.x      = 0
        self.y      = 0

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

    def show3 (self, pen, msg, x, y, size):
        chars   = self.characters
        size    = size/self.height
        ctx     = TextContext(pen)

        pen.use()
        pen.set_origin_scale(x, y, size)
        for c in msg:
            chars[c].show(ctx)

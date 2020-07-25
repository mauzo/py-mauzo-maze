# overlay.py - the HUD overlay

from    OpenGL.GL       import *

from    .           import drawing as dr
from    .geometry   import *
from    .           import gl
from    .           import text

class Overlay:
    __slots__ = [
        "app",      # our app
        "display",  # our display
        "font",     # our font
        "key",      # the key model
        "player",   # the player
        "shader",   # our shader program
        "pen",      # for drawing the text
    ]

    def __init__ (self, app):
        self.app        = app
        self.display    = app.display
        self.player     = app.player

    def init (self):
        text.init()
        self.font   = text.GLFont("stencil.ttf", 100)
        self.key    = self.app.render.load_model("key")

        slc         = gl.ShaderCompiler()
        self.shader = slc.build_shader(vert="plain", frag="overlay")
        self.pen    = text.Pen(slc)
        slc.delete()

    def render (self, ctx):
        glPushAttrib(GL_ENABLE_BIT|GL_TEXTURE_BIT)
        glDisable(GL_DEPTH_TEST)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND)

        self.render_pause(ctx)
        self.render_key(ctx)
        self.render_heart(ctx)

        glPopAttrib()

    def render_pause (self, ctx):
        if not self.app.option("pause"):
            return

        proj    = self.display.overlay
        pen     = self.pen

        pen.use()
        pen.set_projection(proj)
        pen.set_color(vec4(1, 0.5, 0, 0.8))
        self.font.show3(pen, "PAUSED", 0, 0, 0.1)

    def render_key (self, ctx):
        if not self.player.have_key:
            return

        prg     = self.shader
        proj    = self.display.overlay
        view    = Id4
        model   = Id4
        model   = glm.translate(model, vec3(0.05, 0.13, 0))
        model   = glm.scale(model, vec3(0.2))
        model   = glm.rotate(model, HALFPI + 0.2, Xneg)
        model   = glm.rotate(model, PI, Zpos)
        normal  = gl.make_normal_matrix(model)

        prg.use()
        prg.u_proj(proj)
        prg.u_view(view)
        prg.u_model(model)
        prg.u_normal_matrix(normal)

        self.key.render(prg)

    def render_heart (self, ctx):

        proj    = self.display.overlay
        pen     = self.pen
    
        pen.use()
        pen.set_projection(proj)
        pen.set_color(vec4(1, 0.5, 0, 0.8))
        self.font.show3(pen, "H" * self.player.hearts, 0, 0.2, 0.1)

        

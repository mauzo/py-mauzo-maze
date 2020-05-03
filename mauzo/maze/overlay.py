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
        slc.delete()

    # Push new GL state suitable for rendering text.
    def push_gl_state (self):
        ortho   = self.display.overlay

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        gl.load_ffp_matrix(ortho)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glPushAttrib(GL_ENABLE_BIT|GL_TEXTURE_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND)

    # Draw the text
    def render (self):
        self.push_gl_state()

        if self.app.option("pause"):
            glColor4f(1, 0.5, 0, 0.8)
            self.font.show("PAUSED", 0, 0, 100)

        self.pop_gl_state()

    # Separate this from .render above as it does GL3 rendering
    def render_gl3 (self, ctx):
        if self.player.have_key:
            prg     = self.shader
            proj    = self.display.overlay
            view    = mat4(1)
            model   = mat4(1)
            model   = glm.translate(model, vec3(30, 100, 0))
            model   = glm.scale(model, vec3(100, 100, 5))
            model   = glm.rotate(model, HALFPI + 0.2, Xneg)
            model   = glm.rotate(model, PI, Zpos)
            normal  = gl.make_normal_matrix(model)

            glPushAttrib(GL_ENABLE_BIT)
            glDisable(GL_DEPTH_TEST)

            prg.use()
            prg.u_proj(proj)
            prg.u_view(view)
            prg.u_model(model)
            prg.u_normal_matrix(normal)

            self.key.render(prg)

            glPopAttrib()

    # Pop the state pushed above.
    def pop_gl_state (self):
        glPopAttrib()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


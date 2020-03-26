# overlay.py - the HUD overlay

from    OpenGL.GL       import *

from    .       import gl
from    .       import text

class Overlay:
    __slots__ = [
        "app",      # our app
        "display",  # our display
        "font",     # our font
        "key",      # the key model
        "player",   # the player
    ]

    def __init__ (self, app):
        self.app        = app
        self.display    = app.display
        self.player     = app.player

    def init (self):
        text.init()
        self.font   = text.GLFont("stencil.ttf", 100)
        #self.key    = self.app.render.load_model("key")

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
        if self.player.have_key:
            glColor4f(0.5, 0.5, 1, 0.8)
            self.font.show("KEY", 0, 100, 40)

        self.pop_gl_state()

    # Pop the state pushed above.
    def pop_gl_state (self):
        glPopAttrib()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


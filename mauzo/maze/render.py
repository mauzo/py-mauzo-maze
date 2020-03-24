# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import gl
from    .           import text

class Renderer:
    __slots__ = [
        "app",          # our app
        "overlay",      # the text overlay

    ]

    def __init__ (self, app):
        self.app        = app
        self.overlay    = text.Overlay(app)

    def init (self):
        gl.init()
        self.overlay.init()

    # This is called to render every frame. We clear the window, position the
    # camera, and then call the display list to draw the world.
    def render (self):
        app = self.app
        gl.clear()
        app.camera.render()
        app.world.render()
        app.player.render()
        self.overlay.render()

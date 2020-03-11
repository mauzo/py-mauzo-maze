# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import camera
from    .           import gl
from    .           import player
from    .           import text
from    .world      import render_world

class Renderer:
    __slots__ = ["app", "font"]

    def __init__ (self, app):
        self.app    = app

        gl.init()
        text.init()
        self.font   = text.GLFont("Stencil", 100)

    # Clear the screen to remove the previous frame.
    def clear (x):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    def overlay (self):
        if self.app.option("pause"):
            text.push_gl_state()
            glColor4f(1, 0.5, 0, 0.8)
            self.font.show("PAUSED", 0, 0)
            text.pop_gl_state()

    # This is called to render every frame. We clear the window, position the
    # camera, and then call the display list to draw the world.
    def render (self):
        self.clear()
        camera.render_camera()
        render_world()
        player.render_player()
        self.overlay()

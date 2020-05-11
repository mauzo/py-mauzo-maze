# display.py - Manipulate the display

import  glfw
import  glm
from    OpenGL.GL       import *
from    OpenGL.GLU      import *

from    .       import app
from    .       import gl

class Display:
    __slots__ = [
        "app",          # our app
        "overlay",      # a projection matrix for the overlay
        "perspective",  # a projection matrix for the perspective view
        "viewport",     # the size of our window
        "window",       # the glfw window handle
    ]

    def __init__ (self, app):
        self.app        = app
        self.viewport   = (1024, 768)

    # Start up glfw and open the window.
    def init (self):
        window = glfw.create_window(*self.viewport, "Maze", None, None);
        if not window:
            raise RuntimeError("failed to create window")

        self.window = window
        glfw.make_context_current(window)
        glfw.swap_interval(1)
        self.set_viewport(*self.viewport)

    def set_viewport (self, w, h):
        self.viewport = (w, h)
        aspect  = w/h

        glViewport(0, 0, w, h)

        self.perspective    = glm.perspective(glm.radians(45), aspect, 1, 100)
        if w > h:
            self.overlay    = glm.ortho(0, aspect, 0, 1, -1, 1)
        else:
            self.overlay    = glm.ortho(0, 1, 0, 1/aspect, -1, 1)

        glMatrixMode(GL_PROJECTION)
        gl.load_ffp_matrix(self.perspective)

        glMatrixMode(GL_MODELVIEW)

    def flip (self):
        glfw.swap_buffers(self.window)

    def should_close (self):
        return glfw.window_should_close(self.window)

    def post_close (self):
        glfw.set_window_should_close(self.window, True)

    def quit (self):
       glfw.destroy_window(self.window) 

# display.py - Manipulate the display

import  glfw
import  glm
from    OpenGL.GL       import *
from    OpenGL.GLU      import *

from    .       import app

class Display:
    __slots__ = [
        "app",          # our app
        "projection",   # the current projection matrix
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

        # Keep this synced with the FFP matrix for now
        self.projection = glm.perspective(45, aspect, 1, 40)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, aspect, 1.0, 40.0)

        glMatrixMode(GL_MODELVIEW)

    def flip (self):
        glfw.swap_buffers(self.window)

    def should_close (self):
        return glfw.window_should_close(self.window)

    def post_close (self):
        glfw.set_window_should_close(self.window, True)

    def quit (self):
       glfw.destroy_window(self.window) 

# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import camera
from    .           import player
from    .world      import render_world

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    camera.render_camera()
    render_world()
    player.render_player()

# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

from    OpenGL.GL   import *

from    .           import display
from    .           import camera
from    .options    import Options
from    .           import player
from    .world      import render_world

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

# Draw a miniview of the ground under our feet. Not very useful...
def render_miniview ():
    display.display_push_miniview()
    glOrtho(-0.5, 0.5, -0.5, 0.5, 0, 1)

    pos = player.pos()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-pos[0], -pos[1], -pos[2])

    render_world()

    display.display_pop_miniview()

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    camera.render_camera()
    render_world()
    player.render_player()

    if (Options["miniview"]):
        render_miniview()
        render_miniview()

# Try a select buffer operation with the current view
def render_try_select (mode):
    glPushAttrib(GL_ENABLE_BIT)
    if mode == "feedback":
        glFeedbackBuffer(4096, GL_3D)
        glRenderMode(GL_FEEDBACK)
    else:
        glSelectBuffer(4096)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(1)
    glDisable(GL_CULL_FACE)

    render()
    buf = glRenderMode(GL_RENDER)
    glPopAttrib()

    if len(buf) == 0:
        print("No", mode, "records!")
    for h in buf:
        if mode == "feedback":
            (typ, *vs) = h
            print(typ, ",", [v.vertex[2] for v in vs])
        else:
            (mn, mx, nms) = h
            print("min", mn, "max", mx, "names", nms,
                Select[nms[0] - 1])


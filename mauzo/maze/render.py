# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

from    OpenGL.GL   import *

from    .           import display
from    .           import camera
from    .options    import Options
from    .           import player
from    .vectors    import *
from    .world      import render_world

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

ORTHO_RADIUS = 0.49

def render_ortho_view (pos, via):
    depth   = vec_norm(via)
    vhat    = vec_unit(via)
    quat    = quat_rotate_from_to(vhat, [0, 0, -1])
    view    = quat_to_matrix(quat, None)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-ORTHO_RADIUS, ORTHO_RADIUS, -ORTHO_RADIUS, ORTHO_RADIUS,
        0.1, depth)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    # Look in the right direction
    glLoadMatrixf(view)
    glTranslatef(-pos[0], -pos[1], -pos[2])

    render_world()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    return (pos, via)

# Draw a miniview of the ground under our feet. Not very useful...
def render_miniview (doit):
    display.display_push_miniview()
    doit()
    display.display_pop_miniview()

# Try a select buffer operation with the current view
def render_try_select (doit):
    glPushAttrib(GL_ENABLE_BIT|GL_TRANSFORM_BIT)
    glSelectBuffer(4096)
    glRenderMode(GL_SELECT)
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    glInitNames()
    glPushName(1)

    (pos, dpos) = doit()

    buf = glRenderMode(GL_RENDER)
    glPopAttrib()

    if len(buf) == 0:
        return
        
    glPushAttrib(GL_CURRENT_BIT|GL_ENABLE_BIT)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    for h in buf:
        (mn, mx, nms) = h
        point = vec_add(pos, vec_mul(dpos, mn))
        glBegin(GL_POINTS)
        glVertex3f(*point)
        glEnd()
    glPopAttrib()

def render_do_select_views (pos, via):
    doit    = lambda: render_ortho_view(pos, via)
    render_miniview(doit)
    render_try_select(doit)

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    camera.render_camera()
    render_world()
    player.render_player()

    if (Options["miniview"]):
        pos     = player.pos()
        render_do_select_views(pos, [0, 0, -2])
        render_do_select_views(pos, [0, -2, 0.1])

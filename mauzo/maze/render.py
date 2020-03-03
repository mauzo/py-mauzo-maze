# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

import  numpy       as np
from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import camera
from    .           import display
from    .           import player
from    .drawing    import draw_ortho_box, draw_points, select_name
from    .options    import Options
from    .vectors    import *
from    .world      import render_world

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def create_miniview (name, pos, via):
    depth   = vec_norm(via)
    vhat    = vec_unit(via)
    quat    = quat_rotate_from_to(vhat, [0, 0, -1])
    view    = quat_to_matrix(quat, None)
    look    = vec_add(pos, via)

    vw = { "name": name, "pos": pos, "via": via, "points": [] }
    vw["ortho"] = [-0.49, 0.49, -0.49, 0.49, 0, depth]

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadMatrixf(view)
    glTranslatef(-pos[0], -pos[1], -pos[2])
    vw["view"] = glGetDoublev(GL_MODELVIEW_MATRIX)
    glPopMatrix()

    vw["view_inv"] = np.linalg.inv(vw["view"])

    return vw

def render_ortho_view (view):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(*view["ortho"])

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadMatrixd(view["view"])

    render_world()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# Draw a miniview of the ground under our feet. Not very useful...
def render_miniview (view):
    display.display_push_miniview()
    render_ortho_view(view)
    display.display_pop_miniview()

# Try a select buffer operation with the current view
def render_try_select (view):
    glPushAttrib(GL_ENABLE_BIT|GL_TRANSFORM_BIT)
    glSelectBuffer(4096)
    glRenderMode(GL_SELECT)
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    glInitNames()
    glPushName(1)
    render_ortho_view(view)
    buf = glRenderMode(GL_RENDER)
    glPopAttrib()

    if len(buf) == 0:
        return
        
    z   = 2.0
    nm  = None
    for h in buf:
        (minz, maxz, nms) = h
        point = vec_add(view["pos"], vec_mul(view["via"], minz))
        print("Select", view["name"], minz, point, select_name(nms[0]))
        view["points"].append(point)

def render_do_miniview (name, pos, via):
    view = create_miniview(name, pos, via)
    render_try_select(view)
    render_miniview(view)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glMultMatrixd(view["view_inv"])
    draw_ortho_box(*view["ortho"])
    glPopMatrix()
    draw_points(view["points"])

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    camera.render_camera()
    render_world()
    player.render_player()

    if (Options["miniview"]):
        pos     = player.pos()
        face    = camera.Camera["walk_quat"]
        render_do_miniview("down", pos, [0, 0, -2])
        render_do_miniview("walk", pos, quat_apply(face, [2, 0, 1]))

# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

import  math
import  numpy       as np
from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import camera
from    .           import display
from    .           import player
from    .drawing    import draw_points, select_name
from    .options    import Options
from    .vectors    import *
from    .world      import *

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def create_miniview (name, pos, via):
    depth   = vec_norm(via)
    vhat    = vec_unit(via)

    #quat    = quat_rotate_from_to(vhat, [0, 0, -1])
    #view    = quat_to_matrix(quat, None)
    #look    = vec_add(pos, via)

    angle   = camera.Camera["angle"][0]

    vw = { "name": name, "pos": pos, "via": via, "points": [] }
    vw["ortho"] = [-0.49, 0.49, -0.49, 0.49, 0, depth]
    vw["clips"] = [(1, -1, 0, 0.7), (-1, 1, 0, 0.7),
                    (1, 1, 0, 0.7), (-1, -1, 0, 0.7)]

#    glMatrixMode(GL_MODELVIEW)
#    glPushMatrix()
#    #glLoadMatrixf(view)
#    glLoadIdentity()
#    # Annoyingly, the camera starts pointing down (-Z).
#    # Rotate so we are pointing down +X with +Z upwards.
#    glRotatef(90, 0, 0, 1)
#    glRotatef(90, 0, 1, 0)
#    glRotate(angle, 0, 0, 1)
#    glTranslatef(-pos[0], -pos[1], -pos[2])
#    vw["view"] = glGetDoublev(GL_MODELVIEW_MATRIX)
#    glPopMatrix()

    vw["pos"]   = pos
    vw["angle"] = -angle

#    vw["view_inv"] = np.linalg.inv(vw["view"])

    return vw

def render_ortho_view (view):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(*view["ortho"])

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    clips = view["clips"]
    #clips = [(1, -1, 0, 0.7), (-1, 1, 0, 0.7),
    #                (1, 1, 0, 0.7), (-1, -1, 0, 0.7)]
    for i in range(len(clips)):
        pl = GL_CLIP_PLANE0 + i
        glClipPlane(pl, clips[i])
        glEnable(pl)

    pos     = view["pos"]
    angle   = view["angle"]
    # Annoyingly, the camera starts pointing down (-Z).
    # Rotate so we are pointing down +X with +Z upwards.
    glRotatef(90, 0, 0, 1)
    glRotatef(90, 0, 1, 0)
    glRotate(angle, 0, 0, 1)
    glTranslatef(-pos[0], -pos[1], -pos[2])
    #glLoadMatrixf(view["view"])

    #draw_floors()
    draw_walls()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# Draw a miniview of the ground under our feet. Not very useful...
def render_miniview (view):
    display.display_push_miniview()
    render_ortho_view(view)
    display.display_pop_miniview()

# Draw a wireframe box. The z values are inverted, since this is for
# drawing ortho frames.
def draw_ortho_box (view):
    (x1, x2, y1, y2, z1, z2)    = view["ortho"]
    (xm, ym, zm)                = ((x1 + x2)/2, (y1 + y2)/2, (z1 + z2)/2)

    clips   = view["clips"]
    points  = [
        (x1, y1, -z1), (x2, y1, -z1), (x2, y2, -z1), (x1, y2, -z1),
        (x1, y1, -z2), (x2, y1, -z2), (x2, y2, -z2), (x1, y2, -z2),
    ]
    faces   = [
        0, 1, 2, 3,     4, 5, 6, 7,
        0, 4, 5, 1,     1, 5, 6, 2,
        2, 6, 7, 3,     3, 7, 4, 0,
    ]

    glPushAttrib(GL_CURRENT_BIT|GL_ENABLE_BIT|GL_POLYGON_BIT|GL_TRANSFORM_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.0, 1.0)
    glDisable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    #glMultMatrixd(view["view_inv"])
    pos     = view["pos"]
    angle   = view["angle"]
    glTranslatef(pos[0], pos[1], pos[2])
    glRotate(angle, 0, 0, -1)
    glRotatef(90, 0, -1, 0)
    glRotatef(90, 0, 0, -1)
    
    for i in range(len(clips)):
        pl = GL_CLIP_PLANE0 + i
        glClipPlane(pl, clips[i])
        glEnable(pl)

    glBegin(GL_QUADS)
    for p in faces:
        glVertex3f(*points[p])
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(xm, ym, -z1)
    glVertex3f(xm, ym, -z2)
    glVertex3f(x1, ym, -zm)
    glVertex3f(x2, ym, -zm)
    glVertex3f(xm, ym, -zm)
    glVertex3f(xm, y2, -zm)
    glEnd()

    glPopMatrix()
    glPopAttrib()

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
        #print("Select", view["name"], minz, point, select_name(nms[0]))
        view["points"].append(point)

def render_do_miniview (name, pos, via):
    view = create_miniview(name, pos, via)
    #render_try_select(view)
    render_miniview(view)
    draw_ortho_box(view)
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
        #render_do_miniview("down", pos, [0, 0, -2])
        render_do_miniview("walk", pos, quat_apply(face, [2, 0, 1]))

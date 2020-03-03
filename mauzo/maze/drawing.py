# drawing.py - Drawing
# These functions draw 3D objects. Most of them are used to build display
# lists rather than called to render every frame.

from    OpenGL.GL       import *

from    .vectors        import *

# Draw a coloured cube around the origin. Not used; for checking on
# camera positioning.
def draw_cube_10():
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0)
    glVertex3f(10, -10, -10)
    glVertex3f(10, 10, -10)
    glVertex3f(10, 10, 10)
    glVertex3f(10, -10, 10)

    glColor3f(0.5, 0, 0)
    glVertex3f(-10, -10, -10)
    glVertex3f(-10, 10, -10)
    glVertex3f(-10, 10, 10)
    glVertex3f(-10, -10, 10)

    glColor3f(0, 1, 0)
    glVertex3f(-10, 10, -10)
    glVertex3f(10, 10, -10)
    glVertex3f(10, 10, 10)
    glVertex3f(-10, 10, 10)

    glColor3f(0, 0.5, 0)
    glVertex3f(-10, -10, -10)
    glVertex3f(10, -10, -10)
    glVertex3f(10, -10, 10)
    glVertex3f(-10, -10, 10)
    
    glColor3f(0, 0, 1)
    glVertex3f(-10, -10, 10)
    glVertex3f(10, -10, 10)
    glVertex3f(10, 10, 10)
    glVertex3f(-10, 10, 10)

    glColor3f(0, 0, 0.5)
    glVertex3f(-10, -10, -10)
    glVertex3f(10, -10, -10)
    glVertex3f(10, 10, -10)
    glVertex3f(-10, 10, -10)
    glEnd()

# This function allocates names to use in selection mode.
Select = ["dummy"]
def new_select_name (n):
    Select.append(n)
    glLoadName(len(Select))

def select_name (n):
    return Select[n - 1]

# Set up for drawing in white with no lights or depth testing.
def _white_no_lights ():
    glPushAttrib(GL_CURRENT_BIT|GL_ENABLE_BIT)
    #glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)

# Draw a list of points, white, with no lighting or depth
def draw_points (points):
    _white_no_lights()
    glBegin(GL_POINTS)
    for p in points:
        glVertex3f(*p)
    glEnd()
    glPopAttrib()

# Draw a wireframe box. The z values are inverted, since this is for
# drawing ortho frames.
def draw_ortho_box (x1, x2 , y1, y2, z1, z2):
    seq = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    (xm, ym, zm) = ((x1 + x2)/2, (y1 + y2)/2, (z1 + z2)/2)
    _white_no_lights()
    glBegin(GL_LINE_LOOP)
    for p in seq:
        glVertex3f(*p, -z1)
    glEnd()
    glBegin(GL_LINE_LOOP)
    for p in seq:
        glVertex3f(*p, -z2)
    glEnd()
    glBegin(GL_LINES)
    for p in seq:
        glVertex3f(*p, -z1)
        glVertex3f(*p, -z2)
    glVertex3f(xm, ym, -z1)
    glVertex3f(xm, ym, -z2)
    glVertex3f(x1, ym, -zm)
    glVertex3f(x2, ym, -zm)
    glEnd()
    glPopAttrib()

# Draw a marker at the origin so we can see where it is.
def draw_origin_marker():
    new_select_name("marker")
    glColor3f(1, 1, 1)

    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()

# Draw a parallelogram. p is the position of one corner. e1,e2 are the
# vectors along the edges.
def draw_pgram (p, e1, e2):
    n = vec_unit(vec_cross(e1, e2)) 

    p1  = vec_add(p, e1)
    p2  = vec_add(p1, e2)
    p3  = vec_add(p, e2)

    glBegin(GL_TRIANGLE_FAN)
    glNormal3d(*n)
    glVertex3d(*p)
    glVertex3d(*p1)
    glVertex3d(*p2)
    glVertex3d(*p3)
    glEnd()

# Draw a parallelepiped. p is the position of one corner. e1,e2,e3 are
# vectors from that corner along the three edges.
# The edges must be specified right-handed for an outward-facing ppiped.
def draw_ppiped (p, e1, e2, e3):
    draw_pgram(p, e1, e2)
    draw_pgram(p, e2, e3)
    draw_pgram(p, e3, e1)

    p   = vec_add(p, vec_add(e1, vec_add(e2, e3)))
    e1  = vec_neg(e1)
    e2  = vec_neg(e2)
    e3  = vec_neg(e3)

    draw_pgram(p, e2, e1)
    draw_pgram(p, e3, e2)
    draw_pgram(p, e1, e3)


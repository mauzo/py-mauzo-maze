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

def draw_tex_square (vlb, vtr, tlb=(0,0), ttr=(1,1)):
    glBegin(GL_QUADS)
    glTexCoord2f(tlb[0], tlb[1])
    glVertex2f(vlb[0], vlb[1])
    glTexCoord2f(ttr[0], tlb[1])
    glVertex2f(vtr[0], vlb[1])
    glTexCoord2f(ttr[0], ttr[1])
    glVertex2f(vtr[0], vtr[1])
    glTexCoord2f(tlb[0], ttr[1])
    glVertex2f(vlb[0], vtr[1])
    glEnd()

# Draw a list of points, white, with no lighting or depth
def draw_points (points):
    glPushAttrib(GL_CURRENT_BIT|GL_ENABLE_BIT)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    for p in points:
        glVertex3f(*p)
    glEnd()
    glPopAttrib()

# Draw a list of coloured large points
def draw_point (colour, pos):
    glPushAttrib(GL_POINT_BIT)
    glPointSize(10)
    glColor3fv(colour)
    glBegin(GL_POINTS)
    glVertex3fv(pos)
    glEnd()
    glPopAttrib()

# Draw a marker at the origin so we can see where it is.
def draw_origin_marker():
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
    _draw_ppiped(p, e1, e2, e3)

    e1n = vec_mul(vec_unit(e1), 0.49)
    e2n = vec_mul(vec_unit(e2), 0.49)
    e3n = vec_mul(vec_unit(e3), 0.49)
    p   = vec_subtract(p, vec_add(e1n, vec_add(e2n, e3n)))
    e1  = vec_add(e1, vec_mul(e1n, 2))
    e2  = vec_add(e2, vec_mul(e2n, 2))
    e3  = vec_add(e3, vec_mul(e3n, 2))

    glPushAttrib(GL_POLYGON_BIT)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    #_draw_ppiped(p, e1, e2, e3)
    glPopAttrib()

def _draw_ppiped (p, e1, e2, e3):
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


# maze.py
# Playing with OpenGL

import pygame
from pygame.locals  import *
from pygame.event   import Event
from OpenGL.GL      import *
from OpenGL.GLU     import *

WINSIZE = (1024, 768)

World = {
    "floors": [
        { "coords":     (-10, -10, 10, 10, -1),
          "colour":     (0.5, 0, 0),
        },
        { "coords":     (-10, 10, 0, 15, -1),
          "colour":     (0, 0.5, 0),
        },
    ],
}

Player = {
    "pos":  [0, -1, 0],
    "dir":  [0, 1, 0],
}

DL = {}

def vec_add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def vec_norm(v):
    return sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def vec_unit(v):
    n = vec_norm(v)
    return (v[0]/n, v[1]/n, v[2]/n)

def vec_dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vec_cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0],)


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

def draw_origin_marker():
    glColor3f(1, 1, 1)

    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()

def draw_floors():
    for f in World["floors"]:
        glBegin(GL_TRIANGLE_FAN)
        glColor(f["colour"])
        (x1, y1, x2, y2, z) = f["coords"]
        glVertex3f(x1, y1, z)
        glVertex3f(x2, y1, z)
        glVertex3f(x2, y2, z)
        glVertex3f(x1, y2, z)
        glEnd()

def init_display():
    pygame.init()
    pygame.display.set_mode(WINSIZE, OPENGL|DOUBLEBUF)

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)

    glPointSize(5)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, WINSIZE[0]/WINSIZE[1], 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

def init_world():
    dl = glGenLists(1)
    glNewList(dl, GL_COMPILE)
    draw_floors()
    draw_origin_marker()
    glEndList()

    DL["world"] = dl

def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def render_camera():
    pos = Player["pos"]
    drc = Player["dir"]
    
    glLoadIdentity()
    gluLookAt(pos[0], pos[1], pos[2],
              pos[0]+drc[0], pos[1]+drc[1], pos[2]+drc[2],
              0, 0, 1)

def render(ticks):
    render_clear()
    render_camera()
    glCallList(DL["world"])

def handle_key(k):
    if k == K_ESCAPE:
        pygame.event.post(Event(QUIT))
    elif k == K_q:
        pygame.event.post(Event(QUIT))
    elif k == K_a:
        player_move(-1, 0)
    elif k == K_d:
        player_move(1, 0)
    elif k == K_w:
        player_move(0, 1)
    elif k == K_s:
        player_move(0, -1)

def player_move (x, y):
    p = Player["pos"]
    p[0] += x
    p[1] += y
    print("Player pos: ", p)

def mainloop():
    clock = pygame.time.Clock()
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                print("FPS: ", clock.get_fps())
                return

            elif event.type == KEYDOWN:
                handle_key(event.key)

        render(pygame.time.get_ticks())
        pygame.display.flip()
        clock.tick(80)

def main():
    "run the maze"
    init_display()

    try:
        init_opengl()
        init_world()

        mainloop()
    finally:
        pygame.display.quit()

main()

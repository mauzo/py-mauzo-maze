
# maze.py
# Playing with OpenGL

from math           import radians, sin, cos, fmod
import pygame
from pygame.locals  import *
from pygame.event   import Event
from OpenGL.GL      import *
from OpenGL.GLU     import *

# Data

WINSIZE = (1024, 768)

World = {
    "floors": [
        { "coords":     (-10, -10, 10, 10, -1),
          "colour":     (0.5, 0, 0),
          "name":       "red",
        },
        { "coords":     (-10, 10, 0, 15, -1),
          "colour":     (0, 0.5, 0),
          "name":       "green",
        },
        { "coords":     (0, 10, 10, 15, -1),
          "colour":     (0, 0, 0.6),
          "name":       "blue",
        },
        { "coords":     (0, 0, 5, 5, 1),
          "colour":     (1, 0, 1),
          "name":       "pink",
        },
    ],
}

Player = {
    "pos":      [0, -1, 0],
    "theta":    0,
    "dir":      [0, 0, 0],
    "speed":    0,
    "jump":     0,
    "falling":  True,
}

DL = {}

# Vector operations

def vec_add(a, b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]

def vec_mul(v, s):
    return [v[0]*s, v[1]*s, v[2]*s]

def vec_norm(v):
    return sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def vec_unit(v):
    n = vec_norm(v)
    return [v[0]/n, v[1]/n, v[2]/n]

def vec_dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vec_cross(a, b):
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]

# Physics

def find_floor_below(v):
    found = None
    for f in World["floors"]:
        c = f["coords"]
        if v[0] < c[0] or v[1] < c[1]:
            continue
        if v[0] > c[2] or v[1] > c[3]:
            continue
        if v[2] < c[4]:
            continue
        if found and c[4] <= found["coords"][4]:
            continue
        found = f
    return found

# Drawing

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

# Init

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

#  Render

def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def render_camera():
    pos = Player["pos"]
    drc = Player["dir"]
    
    glLoadIdentity()
    gluLookAt(pos[0], pos[1], pos[2]+1, # player is 1 unit tall
              pos[0]+drc[0], pos[1]+drc[1], pos[2]+drc[2]+1,
              0, 0, 1)

def render(ticks):
    render_clear()
    render_camera()
    glCallList(DL["world"])

# Player

def init_player():
    player_turn(0)

def player_turn(by):
    th = Player["theta"]
    # This fmod() function divides by 360 and takes the remainder. It
    # makes sure we are always between 0 and 360 degrees.
    th = fmod(th + by, 360)
    Player["theta"] = th

    d = Player["dir"]
    d[0] = cos(radians(th))
    d[1] = sin(radians(th))

    print("Player direction:", th, "vector:", d)

def player_walk(by):
    d = Player["dir"]
    d = vec_mul(d, by)
    player_move(d)

Speed = {
    "walk":     0.1,
    "jump":     0.1,
    "fall":     0.1,
}

def player_set_speed (to):
    Player["speed"] = to * Speed["walk"]

def player_set_jump (to):
    Player["jump"] = to

def player_move(v):
    p = Player["pos"]
    p = vec_add(p, v)
    Player["pos"] = p

    f = find_floor_below(p)
    print("Player pos:", p, "floor:", (f["name"] if f else "<none>"))

def find_floor_z (pos):
    f = find_floor_below(pos)
    if (f):
        return f["coords"][4] + 0.01
    else:
        return None

def player_physics(ticks):
    pos = Player["pos"]
    drc = Player["dir"]
    spd = Player["speed"]
    jmp = Player["jump"]

    falling     = False
    fall_speed  = Speed["fall"]

    floor_z = find_floor_z(pos)
    if (not floor_z or pos[2] > floor_z):
        falling = True
        
    if (jmp):
        oldz = pos[2]
        pos = vec_add(pos, (0, 0, Speed["jump"]))
    elif (falling):
        oldz = pos[2]
        pos = vec_add(pos, (0, 0, -fall_speed))
    elif (spd != 0):
        pos = vec_add(pos, vec_mul(drc, spd))

    if (floor_z and pos[2] < floor_z):
        pos[2] = floor_z

    if (pos[2] < -20):
        print("AAAAAAAAAAAAARGH!!")
        pygame.event.post(Event(QUIT))
        
    Player["pos"] = pos

# Events

def handle_key(k, down):
    if k == K_ESCAPE:
        pygame.event.post(Event(QUIT))
    elif k == K_q:
        pygame.event.post(Event(QUIT))
    elif k == K_a:
        player_turn(5)
    elif k == K_d:
        player_turn(-5)
    elif k == K_w:
        if (down):
            player_set_speed(1)
        else:
            player_set_speed(0)
    elif k == K_s:
        if (down):
            player_set_speed(-1)
        else:
            player_set_speed(0)
    elif k == K_i:
        if (down):
            player_set_jump(True)
        else:
            player_set_jump(False)
        
def mainloop():
    clock = pygame.time.Clock()
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                print("FPS: ", clock.get_fps())
                return

            elif event.type == KEYDOWN:
                handle_key(event.key, True)

            elif event.type == KEYUP:
                handle_key(event.key, False)

        render(pygame.time.get_ticks())
        pygame.display.flip()

        player_physics(clock.get_time())
        
        clock.tick(80)

# Main

def main():
    "run the maze"
    init_display()

    try:
        init_opengl()
        init_world()
        init_player()

        mainloop()
    finally:
        pygame.display.quit()

main()

# walls
# Jump through platforms
# Move whle jumping

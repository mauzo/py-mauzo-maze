
# maze.py
# Playing with OpenGL

from math           import radians, sin, cos, fmod
import pygame
from pygame.locals  import *
from pygame.event   import Event
from OpenGL.GL      import *
from OpenGL.GLU     import *

# Data

# Information about the display.
Display = {
    # The size of window we open.
    "winsize":  (1024, 768),
    # The framerate we are aiming for.
    "fps":      80,
}

# This defines the world (the level layout).
World = {
    # A list of all the floors. Floors are horizontal rectangles. Each
    # floor has a dict with these keys:
    #   coords      A tuple of (x1, y1, x2, y2, z) defining the rectangle
    #   colour      A tuple of (red, green, blue)
    #   win         True if this is a winning platform, False otherwise
    "floors": [
        { "coords":     (-10, -10, 10, 10, -1),
          "colour":     (0.5, 0, 0),
          "win":        False,
        },
        { "coords":     (-10, 10, 0, 15, -1),
          "colour":     (0, 0.5, 0),
          "win":        False,
        },
        { "coords":     (0, 10, 10, 15, -1),
          "colour":     (0, 0, 0.6),
          "win":        False,
        },
        { "coords":     (0, 0, 5, 5, 2),
          "colour":     (1, 0, 1),
          "win":        False,
        },
        { "coords":     (0, 6, 5, 11, 4),
          "colour":     (1, 1, 0),
          "win":        False,
        },
        { "coords":     (0, 10, 5, 11, 7),
          "colour":     (1, 1, 1),
          "win":        True,
        }
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}

# This dict has information about the player.
Player = {
    # Our current position
    "pos":      [0, -1, 0],
    # Our current veolcity (our speed in the X, Y and Z directions)
    "vel":      [0, 0, 0],
    # The direction we are facing, in degrees CCW from the +ve X-axis
    "theta":    0,
    # The direction we are facing, as a vector of length 1. This is
    # kept up-to-date by player_turn.
    "dir":      [0, 0, 0],
    # The speed we want to be walking (in the direction 'dir'). We
    # only actually walk if we are on a floor.
    "speed":    0,
    # True if we are currently jumping.
    "jump":     False,
}

# The speeds at which the player walks, jumps and falls.
# These are not in sensible units at the moment.
Speed = {
    "walk":     0.1,
    "jump":     0.4,
    "fall":     0.02,
}

# This holds display list numbers, to be used by the render functions.
DL = {}

# Vector operations
# These are mathematical operations on 3D vectors. Maybe we should be using
# a library instead?
# Vectors are represented as 3-element lists. Currently passing in a 3-element
# tuple will work as well.

# Add two vectors
def vec_add(a, b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]

# Multiply a vector by a number
def vec_mul(v, s):
    return [v[0]*s, v[1]*s, v[2]*s]

# Find the length of a vector
def vec_norm(v):
    return sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

# Find a vector of length 1 in the same direction as v
def vec_unit(v):
    n = vec_norm(v)
    return [v[0]/n, v[1]/n, v[2]/n]

# Vector dot product
def vec_dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

# Vector cross product
def vec_cross(a, b):
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]

# Physics

# Find the floor below a given position.
# v is the point in space we want to start from.
# Returns one of the dictionaries from World["floors"], or None.
# This assumes floors are horizontal rectangles.
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
# These functions draw 3D objects. Most of them are used to build display
# lists rather than called to render every frame.

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

# Draw the floors out of World["floors"]. This breaks each rectangle into
# two triangles but doesn't subdivide any further; this will probably need
# changing when we get lights and/or textures.
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
# Initialise various parts of the game.

# Start up pygame and open the window.
def init_display():
    pygame.init()
    pygame.display.set_mode(Display["winsize"], OPENGL|DOUBLEBUF)

# Set up the initial OpenGL state, including the projection matrix.
def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)

    glPointSize(5)

    winsize = Display["winsize"]
    aspect  = winsize[0]/winsize[1]

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, aspect, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# Build a display list representing the world, so we don't have to
# calculate all the triangles every frame.
def init_world():
    dl = glGenLists(1)
    glNewList(dl, GL_COMPILE)
    draw_floors()
    draw_origin_marker()
    glEndList()

    DL["world"] = dl

# Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

# Position the camera based on the player's current position. We put
# the camera 1 unit above the player's position.
def render_camera():
    pos = Player["pos"]
    drc = Player["dir"]
    
    glLoadIdentity()
    gluLookAt(pos[0], pos[1], pos[2]+1,
              pos[0]+drc[0], pos[1]+drc[1], pos[2]+drc[2]+1,
              0, 0, 1)

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    render_camera()
    glCallList(DL["world"])

# Player

# When we start we need to set up Player["dir"] based on Player["theta"],
# so call player_turn to do this.
def init_player():
    player_turn(0)

# The player has died...
def player_die ():
    print("AAAARGH!!!")
    event_post_quit()

# The player has won...
def player_win ():
    print("YaaaY!!!!")

# Turn the player. Changes theta and updates dir to point in the new
# direction. 'by' is the angle in degrees CCW to turn the player by. 
def player_turn(by):
    th = Player["theta"]
    
    # This fmod() function divides by 360 and takes the remainder. It
    # makes sure we are always between 0 and 360 degrees.
    th = fmod(th + by, 360)
    Player["theta"] = th

    # Calculate the new direction vector.
    d = Player["dir"]
    d[0] = cos(radians(th))
    d[1] = sin(radians(th))

    print("Player direction:", th, "vector:", d)

# Set the speed we're trying to walk. We will only move if we're on the
# ground.
def player_set_speed (to):
    Player["speed"] = to * Speed["walk"]

# Set the flag to show we're jumping. We will only jump if we're on the
# ground.
def player_set_jump (to):
    Player["jump"] = to

def player_physics(ticks):
    pos     = Player["pos"]
    vel     = Player["vel"]
    face    = Player["dir"]
    speed   = Player["speed"]
    jump    = Player["jump"]

    # Assume we are falling.
    falling = True

    # Find the floor below us. If there is a floor, and we are close
    # enough to it, we are not falling.
    floor = find_floor_below(pos)
    if (floor):
        floor_z = floor["coords"][4] + 0.01
        if (pos[2] <= floor_z):
            falling = False

    if (falling):
        # If we are falling, increase our velocity in the downwards z direction
        # by the fall speed (actually an acceleration). 
        vel[2] -= Speed["fall"]
    else:
        # Otherwise, start by multiplying our direction vector by our
        # walk speed (which might be negative to walk backwards).
        vel = vec_mul(face, speed)
        # Then, if we are jumping, set our z velocity to be the jump speed
        # and turn off the jump (we only jump once).
        if (jump):
            vel[2] = Speed["jump"]
            Player["jump"] = False

    # Take the velocity vector we have calculated and add it to our position
    # vector to give our new position.
    pos = vec_add(pos, vel)    

    # If we have fallen through the floor put us back on top of the floor
    # so that we land on it.
    if (floor and pos[2] < floor_z):
        pos[2] = floor_z

    # If we fall too far we die.
    if (pos[2] < World["doom_z"]):
        player_die()

    # Save our position and velocity for next time.        
    Player["pos"] = pos
    Player["vel"] = vel

# Events
# These functions manage things that happen while the program is running.

# Tell pygame we want to quit.
def event_post_quit ():
    pygame.event.post(Event(QUIT))

# Handle a key-up or key-down event. k is the keycode, down is True or False.
def handle_key(k, down):
    if k == K_ESCAPE:
        event_post_quit()
    elif k == K_q:
        event_post_quit()
    elif k == K_LEFT:
        player_turn(5)
    elif k == K_RIGHT:
        player_turn(-5)
    elif k == K_UP:
        if (down):
            player_set_speed(1)
        else:
            player_set_speed(0)
    elif k == K_DOWN:
        if (down):
            player_set_speed(-1)
        else:
            player_set_speed(0)
    elif k == K_SPACE:
        # We don't need to clear jump on keyup, this happens automatically
        # after we jump.
        if (down):
            player_set_jump(True)

# This is the main loop that runs the whole game. We wait for events
# and handle them as we need to.
def mainloop():
    # Set up a clock to keep track of the framerate.
    clock   = pygame.time.Clock()    
    fps     = Display["fps"]
    
    while True:
        # Check for events and deal with them.
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                print("FPS: ", clock.get_fps())
                return

            elif event.type == KEYDOWN:
                handle_key(event.key, True)

            elif event.type == KEYUP:
                handle_key(event.key, False)

        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        render()
        pygame.display.flip()

        # Run the physics. Pass in the time taken since the last frame.
        player_physics(clock.get_time())

        # Wait if necessary so that we don't draw more frames per second
        # than we want. Any more is just wasting processor time.
        clock.tick(fps)

# Main

def main():
    # Open the window and setup pygame
    init_display()

    # This try: block catches errors and makes sure the finally: block
    # runs even if there's an error. Otherwise the window doesn't go away.
    try:
        # Run the other initialisation
        init_opengl()
        init_world()
        init_player()

        # Go into the main loop, which doesn't return until we quit the game.
        mainloop()
    finally:
        # Make sure the window is closed when we finish.
        pygame.display.quit()

main()

# walls
# Jump through platforms
# hold a direction


# maze.py
# Playing with OpenGL

from math           import radians, sin, cos, fmod, pi
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
          "win":        True,
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
        { "coords":     (6, 6, 12, 11, 6),
          "colour":     (1, 1, 1),
          "win":        False,
        }
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}

# This dict has information about the camera. The camera moves with the
# player but has its own direction. Most of these values are just dummies
# which will be set up by camera_init.
Camera = {
    # Are we up to date with the player position?
    "uptodate": False,
    # Where is the camera position, relative to the player position?
    "offset":   [0, 0, 1],
    # The current position of the camera.
    "pos":      [0, 0, 0],
    # The current camera angle, horizontal and vertical.
    "angle":    [0, 0],
    # The vector the player walks along.
    "walk_vec": [0, 0, 0],
    # The vector the player walks sideways along.
    "strafe_vec": [0, 0, 0],
}
    
# This dict has information about the player.
Player = {
    # Our current position
    "pos":      [-1, 0, 0],
    # Our current veolcity (our speed in the X, Y and Z directions)
    "vel":      [0, 0, 0],
    # Our current walk speed.
    "walk":     0,
    # Our current strafe speed.
    "strafe":   0,
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

FLOOR_THICKNESS = 0.2

# Draw the floors out of World["floors"]. This breaks each rectangle into
# two triangles but doesn't subdivide any further; this will probably need
# changing when we get lights and/or textures.
def draw_floors ():
    for f in World["floors"]:
        (x1, y1, x2, y2, z) = f["coords"]
        glColor(f["colour"])
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x1, y1, z)
        glVertex3f(x2, y1, z)
        glVertex3f(x2, y2, z)
        glVertex3f(x1, y2, z)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x1, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y2, z-FLOOR_THICKNESS)
        glVertex3f(x1, y2, z-FLOOR_THICKNESS)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x1, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y1, z)
        glVertex3f(x1, y1, z)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x1, y2, z)
        glVertex3f(x2, y2, z)
        glVertex3f(x2, y2, z-FLOOR_THICKNESS)
        glVertex3f(x1, y2, z-FLOOR_THICKNESS)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x1, y1, z-FLOOR_THICKNESS)
        glVertex3f(x1, y2, z-FLOOR_THICKNESS)
        glVertex3f(x1, y2, z)
        glVertex3f(x1, y2, z)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x2, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y2, z-FLOOR_THICKNESS)
        glVertex3f(x2, y2, z)
        glVertex3f(x2, y2, z)
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
    #draw_cube_10()
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
    pos     = Camera["pos"]
    angle   = Camera["angle"]
    
    # Clear the previous camera position
    glLoadIdentity()
    # Annoyingly, the camera starts pointing down (-Z).
    # Rotate so we are pointing down +X with +Y upwards.
    glRotatef(90, 0, 0, 1)
    glRotatef(90, 0, 1, 0)

    # Set the new camera position for this frame. Everything has to be
    # done backwards because we are moving the world rather than moving
    # the camera. This is why we rotate before we translate rather than
    # the other way round.
    
    # Vertical rotation. We are pointing down +X so we would expect a
    # CCW rotation about -Y to make +ve angles turn upwards, but as
    # everthing is backwards we need to turn the other way.
    glRotatef(angle[1], 0, 1, 0)
    # Horizontal rotation. Again we rotate about -Z rather than +Z.
    glRotatef(angle[0], 0, 0, -1)
    # Move to the camera position. These need to be negative because we
    # are moving the world rather than moving the camera.
    glTranslatef(-pos[0], -pos[1], -pos[2])

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    render_camera()
    glCallList(DL["world"])

# Camera

# Tell the camera it needs to update itself
def camera_needs_update ():
    Camera["uptodate"] = False

# Update the vectors for moving the player.
def camera_update_movement_vectors ():
    angle   = Camera["angle"]

    # This is the angle we walk along, in radians
    walk    = radians(angle[0])

    # This is the angle we walk sideways along
    strafe  = walk - pi/2

    # This is the direction we walk forwards
    Camera["walk_vec"] = [cos(walk), sin(walk), 0]

    # This is the direction we walk right
    Camera["strafe_vec"] = [cos(strafe), sin(strafe), 0]

    print("Camera angle", angle)
    #print("New vectors walk", Camera["walk_vec"],
    #        "strafe", Camera["strafe_vec"])
    
    camera_needs_update()

# Look up or down.
def camera_look_updown (by):
    angle = Camera["angle"]
    
    new = angle[1] + by
    if (new > 90):
        new = 90
    if (new < -90):
        new = -90
    angle[1] = new

    print("New camera angle", angle)    
    camera_needs_update()

# Look left or right. -ve means look left.
def camera_look_leftright (by):
    angle = Camera["angle"]

    # This fmod() function divides by 360 and takes the remainder.
    # This makes sure we are always between 0 and 360 degrees.
    # We subtract 'by' because angles are measured CCW but we want
    # a +ve 'by' to turn us right. Otherwise it's confusing.
    angle[0] = fmod(angle[0] - by, 360)
    if (angle[0] < 0):
        angle[0] += 360
    
    camera_update_movement_vectors()

# Update the camera position based on the player position
def camera_update_position ():
    # If we are already up to date there is nothing to do
    if (Camera["uptodate"]):
        return

    # Find our position from the player position and our offset.
    pos = vec_add(Player["pos"], Camera["offset"])
    Camera["pos"] = pos

    print("Camera position", pos)

    Camera["uptodate"] = True

def camera_init ():
    camera_update_movement_vectors()
    camera_update_position()

def camera_physics ():
    camera_update_position()

# Player

# Nothing to do at the moment.
def init_player():
    pass

# The player has died...
def player_die ():
    print("AAAARGH!!!")
    event_post_quit()

# The player has won...
def player_win ():
    print("YaaaY!!!!")
    event_post_quit()

# Set the speed we're trying to walk. We will only move if we're on the
# ground.
def player_walk (to):
    Player["walk"] = to * Speed["walk"]

# Set the speed we're trying to walk sideways. 
def player_strafe (to):
    Player["strafe"] = to * Speed["walk"]

# Set the flag to show we're jumping. We will only jump if we're on the
# ground.
def player_jump (to):
    Player["jump"] = to

def player_physics(ticks):
    pos     = Player["pos"]
    vel     = Player["vel"]
    walk    = Player["walk"]
    strafe  = Player["strafe"]
    jump    = Player["jump"]

    walk_vec    = Camera["walk_vec"]
    strafe_vec  = Camera["strafe_vec"]

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
        # Otherwise, start by multiplying our walk vector by our
        # walk speed (which might be negative to walk backwards).
        vel = vec_mul(walk_vec, walk)
        # Then add our strafe (sideways) vector.
        vel = vec_add(vel, vec_mul(strafe_vec, strafe))
        # Then, if we are jumping, set our z velocity to be the jump speed
        # and turn off the jump (we only jump once).
        if (jump):
            vel[2] = Speed["jump"]
            player_jump(False)

    # Save our velocity for next time
    Player["vel"] = vel

    # If there is nothing to do, return
    if (vel[0] == 0 and vel[1] == 0 and vel[2] == 0):
        return

    # Take the velocity vector we have calculated and add it to our position
    # vector to give our new position.
    pos = vec_add(pos, vel)    

    # If we have fallen through the floor put us back on top of the floor
    # so that we land on it.
    if (floor and pos[2] < floor_z):
        pos[2] = floor_z

    print("Player move from", Player["pos"], "to", pos)

    # If we fall too far we die.
    if (pos[2] < World["doom_z"]):
        player_die()

    # Save our new position and tell the camera we've moved.
    Player["pos"] = pos
    camera_needs_update()

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
        
    elif k == K_i:
        camera_look_updown(5)
    elif k == K_k:
        camera_look_updown(-5)
    elif k == K_j:
        camera_look_leftright(-5)
    elif k == K_l:
        camera_look_leftright(5)
        
    elif k == K_w:
        if (down):
            player_walk(1)
        else:
            player_walk(0)
    elif k == K_s:
        if (down):
            player_walk(-1)
        else:
            player_walk(0)
    elif k == K_a:
        if (down):
            player_strafe(-1)
        else:
            player_strafe(0)
    elif k == K_d:
        if (down):
            player_strafe(1)
        else:
            player_strafe(0)
    elif k == K_SPACE:
        # We don't need to clear jump on keyup, this happens automatically
        # after we jump.
        if (down):
            player_jump(True)

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
        camera_physics()

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
        camera_init()

        # Go into the main loop, which doesn't return until we quit the game.
        mainloop()
    finally:
        # Make sure the window is closed when we finish.
        pygame.display.quit()

main()

# walls
# Jump through platforms
# hold a direction
#looking up and down

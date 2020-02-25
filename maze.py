
# maze.py
# Playing with OpenGL

from math           import fmod
import numpy        as np
from OpenGL.GL      import *
from OpenGL.GLU     import *
import pygame
from pygame.locals  import *
from pygame.event   import Event

# I have started moving pieces into their own files.
from mauzo.maze.vectors   import *

# Data

# Information about the display.
Display = {
    # The size of window we open.
    "winsize":  (1024, 768),
    # The framerate we are aiming for.
    "fps":      80,
}

# This defines what all the keys do. Each keycode maps to a 2-element tuple;
# the first says what to do on keydown, the second what to do on keyup.
# The names are looked up as functions in the current module.
Key_Bindings = {
    K_ESCAPE:   (["event_post_quit"],           None),
    K_q:        (["event_post_quit"],           None),
    K_i:        (["camera_pan", [0, 1]],        ["camera_pan", [0, -1]]),
    K_k:        (["camera_pan", [0, -1]],       ["camera_pan", [0, 1]]),
    K_j:        (["camera_pan", [-1, 0]],       ["camera_pan", [1, 0]]),
    K_l:        (["camera_pan", [1, 0]],        ["camera_pan", [-1, 0]]),
    K_w:        (["player_walk", [1, 0, 0]],    ["player_walk", [-1, 0, 0]]),
    K_s:        (["player_walk", [-1, 0, 0]],   ["player_walk", [1, 0, 0]]),
    K_a:        (["player_walk", [0, 1, 0]],    ["player_walk", [0, -1, 0]]),
    K_d:        (["player_walk", [0, -1, 0]],   ["player_walk", [0, 1, 0]]),
    K_SPACE:    (["player_jump", True],         None),
    K_F2:       (["toggle", "wireframe"],       None),
    K_F3:       (["toggle", "backface"],        None),
}

# This defines the world (the level layout).
World = {
    # All the colours we use.
    "colours": {
        "Blue":     (0, 0, 0.5),
        "Green":    (0, 0.5, 0),
        "Red":      (0.5, 0, 0),
        "Grey":     (1, 1, 0.5),
        "Pink":     (1, 0, 1),
        "White":    (1, 1, 1),
        "Yellow":   (1, 1, 0),
    },

    # A list of all the floors. Floors are horizontal rectangles. Each
    # floor has a dict with these keys:
    #   coords      A tuple of (x1, y1, x2, y2, z) defining the rectangle
    #   colour      A tuple of (red, green, blue)
    #   win         True if this is a winning platform, False otherwise
    "floors": [
        { "coords":     (-10, -10, 10, 10, -1),
          "colour":     "Red",
          "win":        False,
        },
        { "coords":     (-10, 10, 0, 15, -1),
          "colour":     "Green",
          "win":        False,
        },
        { "coords":     (0, 10, 10, 15, -1),
          "colour":     "Blue",
          "win":        False,
        },
        { "coords":     (0, 0, 5, 5, 2),
          "colour":     "Yellow",
          "win":        False,
        },
        { "coords":     (0, 6, 5, 11, 4),
          "colour":     "Pink",
          "win":        False,
        },
        { "coords":     (6, 6, 12, 11, 6),
          "colour":     "White",
          "win":        True,
        },
        { "coords":     (-10, 10, 5, 15, 3),
          "colour":     "Grey",
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
    # Where is the camera position, relative to the player position?
    "offset":   [0, 0, 1],
    # The current position of the camera.
    "pos":      [0, 0, 0],
    # The current camera angle, horizontal and vertical.
    "angle":    [70, 0],
    # The current pan speeds
    "pan":      [0, 0],
    # The horizontal camera angle as a quaternion
    "walk_quat": [0, 0, 0, 0],
}
    
# This dict has information about the player.
Player = {
    # Our current position
    "pos":      [-4, -8, 0],
    # Our current veolcity (our speed in the X, Y and Z directions)
    "vel":      [0, 0, 0],
    # Our current walk speed.
    "walk":     [0, 0, 0],
    # True if we are currently jumping.
    "jump":     False,
    # Have we moved this frame?
    "moved":    True,
}

# This holds options which can be changed at runtime
Options = {
    # Display in wireframe
    "wireframe":    False,
    # Show back faces
    "backface":     False,
}

# The speeds at which the player walks, jumps and falls.
# These are not in sensible units at the moment.
Speed = {
    "walk":     0.1,
    "jump":     0.4,
    "fall":     0.02,
    "pan":      0.8,
}

# This holds display list numbers, to be used by the render functions.
DL = {}

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
    col = World["colours"]
    for f in World["floors"]:
        (x1, y1, x2, y2, z) = f["coords"]
        colname = f["colour"]
        glColor(col[colname])
        
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(x1, y1, z)
        glVertex3f(x2, y1, z)
        glVertex3f(x2, y2, z)
        glVertex3f(x1, y2, z)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(x1, y1, z-FLOOR_THICKNESS)
        glVertex3f(x1, y2, z-FLOOR_THICKNESS)
        glVertex3f(x2, y2, z-FLOOR_THICKNESS)
        glVertex3f(x2, y1, z-FLOOR_THICKNESS)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, -1, 0)
        glVertex3f(x1, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y1, z)
        glVertex3f(x1, y1, z)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(x1, y2, z)
        glVertex3f(x2, y2, z)
        glVertex3f(x2, y2, z-FLOOR_THICKNESS)
        glVertex3f(x1, y2, z-FLOOR_THICKNESS)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(-1, 0, 0)
        glVertex3f(x1, y1, z-FLOOR_THICKNESS)
        glVertex3f(x1, y1, z)
        glVertex3f(x1, y2, z)
        glVertex3f(x1, y2, z-FLOOR_THICKNESS)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(1, 0, 0)
        glVertex3f(x2, y1, z-FLOOR_THICKNESS)
        glVertex3f(x2, y2, z-FLOOR_THICKNESS)
        glVertex3f(x2, y2, z)
        glVertex3f(x2, y1, z)
        glEnd()

def draw_world_lights ():
    glLightfv(GL_LIGHT0, GL_AMBIENT,    [0.3, 0.3, 0.3, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,    [0.7, 0.7, 0.7, 1])
    glLightfv(GL_LIGHT0, GL_POSITION,   [0.3, -1.2, 0.4, 0])

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
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHT0)
    glEnable(GL_CULL_FACE)

    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

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
    draw_world_lights()
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
    # Rotate so we are pointing down +X with +Z upwards.
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

# Options

# Toggle an option
def toggle (o):
    # Change the options
    Options[o] = not Options[o]

    # Check if we have an update function and call it
    func = "option_" + o
    if (func in globals()):
        f = globals()[func]
        f(Options[o])

def option_wireframe (on):
    if (on):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

def option_backface (on):
    if (on):
        glDisable(GL_CULL_FACE)
        # Display back faces bright cyan
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1)
        glMaterialfv(GL_BACK, GL_EMISSION, [0, 1, 1])
    else:
        glEnable(GL_CULL_FACE)

# Camera

# Change the camera pan speed
def camera_pan (v):
    Camera["pan"][0] += v[0] * Speed["pan"]
    Camera["pan"][1] += v[1] * Speed["pan"]

def camera_init ():
    camera_update_walk_quat()

def camera_update_walk_quat ():
    angle = Camera["angle"]
    Camera["walk_quat"] = quat_rotate_about(angle[0], [0, 0, 1])
    print("Camera angle", angle, "quat", Camera["walk_quat"])

# Update the camera angle if we are panning.
def camera_do_pan ():
    pan     = Camera["pan"]
    if (pan == [0, 0]):
        return

    angle   = Camera["angle"]

    # This fmod() function divides by 360 and takes the remainder.
    # This makes sure we are always between 0 and 360 degrees.
    # We subtract pan[0] because angles are measured CCW but we want
    # a +ve pan to turn us right. Otherwise it's confusing.
    horiz = fmod(angle[0] - pan[0], 360)
    if (horiz < 0):
        horiz += 360
    
    vert = angle[1] + pan[1]
    if (vert > 90):
        vert = 90
    if (vert < -90):
        vert = -90

    Camera["angle"]     = [horiz, vert]
    camera_update_walk_quat()

# Move the camera if we need to.
def camera_physics ():
    if (Player["moved"]):
        # Find our position from the player position and our offset.
        pos = vec_add(Player["pos"], Camera["offset"])
        Camera["pos"] = pos
    
    camera_do_pan()


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

# Set how we're trying to walk. We will only move if we're on the
# ground. Don't attempt to set a Z coordinate
def player_walk (v):
    Player["walk"] = vec_add(Player["walk"], vec_mul(v, Speed["walk"]))

# Set the flag to show we're jumping. We will only jump if we're on the
# ground.
def player_jump (to):
    Player["jump"] = to

def player_physics(ticks):
    pos     = Player["pos"]
    vel     = Player["vel"]
    walk    = Player["walk"]
    jump    = Player["jump"]

    walk_q  = Camera["walk_quat"]

    # Assume we are falling.
    falling = True

    # Find the floor below us. If there is a floor, and we are close
    # enough to it, we are not falling.
    floor = find_floor_below(pos)
    if (floor):
        floor_z = floor["coords"][4] + 0.01
        if (pos[2] <= floor_z):
            falling = False
            if (floor["win"]):
                player_win()

    if (falling):
        # If we are falling, increase our velocity in the downwards z direction
        # by the fall speed (actually an acceleration). 
        vel[2] -= Speed["fall"]
    else:
        # Otherwise, set our velocity to our walk vector rotated to the
        # camera angle.
        vel = quat_apply(walk_q, walk)
        # Then, if we are jumping, set our z velocity to be the jump speed
        # and turn off the jump (we only jump once).
        if (jump):
            vel[2] = Speed["jump"]
            player_jump(False)

    # Save our velocity for next time
    Player["vel"] = vel

    # If we aren't moving, tell the camera we haven't moved and return.
    if (vel == [0, 0, 0]):
        Player["moved"] = False
        return

    # Tell the camera we have moved.
    Player["moved"] = True

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

    # Save our new position.
    Player["pos"] = pos

# Events
# These functions manage things that happen while the program is running.

# Tell pygame we want to quit.
def event_post_quit ():
    pygame.event.post(Event(QUIT))

# Handle a key-up or key-down event. k is the keycode, down is True or False.
def handle_key(k, down):
    # If the keycode is not in our dict, we have nothing to do.
    if (k not in Key_Bindings):
        return

    # Find the entry for the keycode, and choose the first part for keydown
    # and the second for keyup. If we have None then there is nothing to do.
    bindings = Key_Bindings[k]
    if (down):
        binding = bindings[0]
    else:
        binding = bindings[1]

    if (binding is None):
        return

    # The first entry in the list is the function name, the rest are the
    # arguments for the function.
    function_name   = binding[0]
    function_args   = binding[1:]

    # Find the function by looking up in the globals() dict.
    function        = globals()[function_name]
    # Call the function, passing the arguments. The * passes the
    # pieces of the list separately, rather than passing the whole list.
    function(*function_args)

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


# maze.py
# Playing with OpenGL

from OpenGL.GL      import *
from OpenGL.GLU     import *
import pygame
from pygame.locals  import *

# I have started moving pieces into their own files.
from mauzo.maze.camera      import *
from mauzo.maze.drawing     import *
from mauzo.maze.events      import *
from mauzo.maze.player      import *
from mauzo.maze.vectors     import *
from mauzo.maze.world       import *

# Data

# Information about the display.
Display = {
    # The size of window we open.
    "viewport": (1024, 768),
    # The framerate we are aiming for.
    "fps":      80,
    # The LHS of the miniview
    "mini_x":   0,
    # The number of miniviews in use
    "mini_n":   0,
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
    K_F4:       (["toggle", "miniview"],        None),
}

# This holds options which can be changed at runtime
Options = {
    # Display in wireframe
    "wireframe":    False,
    # Show back faces
    "backface":     False,
    # Show miniviews
    "miniview":     False,
}

# This holds display list numbers, to be used by the render functions.
DL = {}

# Init
# Initialise various parts of the game.

# Start up pygame and open the window.
def init_display():
    pygame.init()
    pygame.display.set_mode(Display["viewport"],
        OPENGL|DOUBLEBUF|RESIZABLE)

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

MINI_SIZE   = 200
MINI_OFF    = 50

# Set up the viewport and projection after a window resize
def display_set_viewport ():
    (w, h)  = Display["viewport"]

    if (Options["miniview"]):
        mini_x  = w - MINI_SIZE
        w       = mini_x - MINI_OFF
        Display["mini_x"] = mini_x
    else:
        Display["mini_x"] = 0

    aspect  = w/h

    glViewport(0, 0, w, h)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, aspect, 1.0, 40.0)
    #glOrtho(-10, 10, 0, 10, 0, 40)

    glMatrixMode(GL_MODELVIEW)

# Reset to the first miniview
def display_reset_miniview ():
    Display["mini_n"] = 0

# Push into the miniview. Leaves GL_PROJECTION selected and cleared.
def display_push_miniview ():
    x   = Display["mini_x"]
    n   = Display["mini_n"]

    y   = n*(MINI_SIZE + MINI_OFF)

    Display["mini_n"] = n + 1

    glPushAttrib(GL_VIEWPORT_BIT|GL_TRANSFORM_BIT|GL_ENABLE_BIT)
    glViewport(x, y, MINI_SIZE, MINI_SIZE)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

# Pop from the miniview. Make sure to balance calls to glPush/PopAttrib
# before calling this.
def display_pop_miniview ():
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glPopAttrib()

# Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

def render_miniview ():
    display_push_miniview()
    glOrtho(-0.5, 0.5, -0.5, 0.5, 0, 1)

    pos = Player["pos"]

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-pos[0], -pos[1], -pos[2])

    render_world()

    display_pop_miniview()

# This is called to render every frame. We clear the window, position the
# camera, and then call the display list to draw the world.
def render():
    render_clear()
    render_camera()
    render_world()
    render_player()

    if (Options["miniview"]):
        render_miniview()
        render_miniview()

# Try a select buffer operation with the current view
def render_try_select (mode):
    glPushAttrib(GL_ENABLE_BIT)
    if mode == "feedback":
        glFeedbackBuffer(4096, GL_3D)
        glRenderMode(GL_FEEDBACK)
    else:
        glSelectBuffer(4096)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(1)
    glDisable(GL_CULL_FACE)

    render()
    buf = glRenderMode(GL_RENDER)
    glPopAttrib()

    if len(buf) == 0:
        print("No", mode, "records!")
    for h in buf:
        if mode == "feedback":
            (typ, *vs) = h
            print(typ, ",", [v.vertex[2] for v in vs])
        else:
            (mn, mx, nms) = h
            print("min", mn, "max", mx, "names", nms,
                Select[nms[0] - 1])

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

def option_miniview (on):
    display_set_viewport()

# Events
# These functions manage things that happen while the program is running.

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

# Handle a window resize event
def handle_resize (w, h):
    print("RESIZE:", w, "x", h)
    Display["viewport"] = (w, h)
    display_set_viewport()

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
                
            elif event.type == VIDEORESIZE:
                handle_resize(event.w, event.h)

        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        render()
        pygame.display.flip()

        # Run the physics. Pass in the time taken since the last frame.
        player_physics(clock.get_time())
        camera_physics()

        # Reset the miniview if necessary
        display_reset_miniview()

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

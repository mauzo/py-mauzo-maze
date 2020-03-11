# display.py - Manipulate the display

from    OpenGL.GL       import *
from    OpenGL.GLU      import *
import  pygame
from    pygame.locals   import *

from    .       import options

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

# Start up pygame and open the window.
def init_display():
    pygame.init()
    pygame.display.set_mode(Display["viewport"],
        OPENGL|DOUBLEBUF|RESIZABLE)

def display_quit ():
    pygame.display.quit()

def display_set_viewport (w, h):
    Display["viewport"] = (w, h)
    display_reset_viewport()

MINI_SIZE   = 200
MINI_OFF    = 50

# Set up the viewport and projection after a window resize
def display_reset_viewport ():
    (w, h)  = Display["viewport"]

    if (options.Options["miniview"]):
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

    glMatrixMode(GL_MODELVIEW)

def display_flip ():
    pygame.display.flip()
    display_reset_miniview()

# Reset to the first miniview
def display_reset_miniview ():
    Display["mini_n"] = 0

# Push into the miniview.
def display_push_miniview ():
    x   = Display["mini_x"]
    n   = Display["mini_n"]

    y   = n*(MINI_SIZE + MINI_OFF)

    Display["mini_n"] = n + 1

    glPushAttrib(GL_VIEWPORT_BIT|GL_TRANSFORM_BIT|GL_ENABLE_BIT)
    glViewport(x, y, MINI_SIZE, MINI_SIZE)

# Pop from the miniview. Make sure to balance calls to glPush/PopAttrib
# before calling this.
def display_pop_miniview ():
    glPopAttrib()


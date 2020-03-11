# options.py - Options the user can change at runtime.

from    OpenGL.GL       import *

from    .   import display

# This holds options which can be changed at runtime.
# This must come before the imports below as .display uses it.
Options = {
    # Display in wireframe
    "wireframe":    False,
    # Show back faces
    "backface":     False,
    # Show miniviews
    "miniview":     False,
    # Toggle fps
    "40fps":        False,
}

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
    display.display_reset_viewport()

def option_40fps (on):
    if on:
        display.Display["fps"] = 40
    else:
        display.Display["fps"] = 80
    print("FPS now", display.Display["fps"])

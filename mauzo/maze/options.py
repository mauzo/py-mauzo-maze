# options.py - Options the user can change at runtime.

from    OpenGL.GL       import *

from    .   import app
from    .   import display

# This holds options which can be changed at runtime.
# This must come before the imports below as .display uses it.
Options = {
    # Toggle fps
    "40fps":        False,
    # Show back faces
    "backface":     False,
    # Show miniviews
    "miniview":     False,
    # Paused
    "pause":        False,
    # Display in wireframe
    "wireframe":    False,
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

# XXX hack We should not be poking inside App like this. Options needs
# to be an object too, but then so does everything else...
def option_40fps (on):
    a = app.get_app()
    if on:
        a.fps = 40
    else:
        a.fps = 80
    print("FPS now", a.fps)

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

def option_pause (on):
    app.get_app().run_physics = not on

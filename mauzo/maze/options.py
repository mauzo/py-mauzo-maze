# options.py - Options the user can change at runtime.

from    OpenGL.GL       import *

from    .   import app
from    .   import display

# This represents a single option
class Option:
    __slots__ = [
        # The option name
        "name",
        # The current value
        "value",
        # A setter callback
        "callback",
    ]

    def __init__ (self, name, value, callback=None):
        self.name       = name
        self.value      = value
        self.callback   = callback

    def set (self, value):
        self.value = value
        print("Set option", self.name, "to", value)
        if self.callback is not None:
            self.callback(value)
            
    def toggle (self):
        self.set(not self.value)

# This temporarily holds the allowed options. Later objects will be able
# to register their own. All options default to False for now.
_OPTS = [
    # Toggle fps
    "40fps",
    # Show back faces
    "backface",
    # Show miniviews
    "miniview",
    # Paused
    "pause",
    # Display in wireframe
    "wireframe",
]

# This holds options which can be changed at runtime.
class Options:
    __slots__ = [
        # Our app
        "app",
        # The allowed options. This is a dict mapping option name to
        # Option objects.
        "options",
    ]

    def __init__ (self, app):
        self.app        = app
        self.options    = {}

        for o in _OPTS:
            f = "option_" + o
            cb = globals()[f] if f in globals() else None
            self.options[o] = Option(o, False, cb)
    
    def get (self, o):
        return self.options[o].value

    def set (self, o, v):
        self.options[o].set(v)

    def toggle (self, o):
        self.options[o].toggle()

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

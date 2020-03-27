# options.py - Options the user can change at runtime.

from    OpenGL.GL       import *

from    .   import app
from    .   import display

# This represents a single option
class Option:
    __slots__ = [
        "name",     # The option name
        "value",    # The current value
        "on",       # callback when the value is True
        "off",      # "" False
    ]

    def __init__ (self, name, **kwargs):
        self.name       = name
        if "value" in kwargs:
            self.value  = kwargs["value"]
        else:
            self.value  = False
        if "on" in kwargs:
            self.on     = kwargs["on"]
        else:
            self.on     = lambda: None
        if "off" in kwargs:
            self.off    = kwargs["off"]
        else:
            self.off    = lambda: None

    def set (self, value):
        self.value = value
        print("Set option", self.name, "to", value)
        if value:
            self.on()
        else:
            self.off()
            
    def toggle (self):
        self.set(not self.value)

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

    def register (self, name, **kwargs):
        self.options[name] = Option(name=name, **kwargs)
    
    def get (self, o):
        return self.options[o].value

    def set (self, o, v):
        self.options[o].set(v)

    def toggle (self, o):
        self.options[o].toggle()


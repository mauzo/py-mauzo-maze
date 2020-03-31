# input.py - Handle user input

import  glfw
from    glm             import vec2, vec3

# For now we have a static list of keybindings. Later we want to move
# this into a file.
_KEYS = [
    ("ESCAPE",   ["quit"],                      None),
    ("Q",        ["quit"],                      None),
    ("I",        ["pan", vec2(0, 1)],           ["pan", vec2(0, -1)]),
    ("K",        ["pan", vec2(0, -1)],          ["pan", vec2(0, 1)]),
    ("J",        ["pan", vec2(-1, 0)],          ["pan", vec2(1, 0)]),
    ("L",        ["pan", vec2(1, 0)],           ["pan", vec2(-1, 0)]),
    ("W",        ["walk", vec3(1, 0, 0)],       ["walk", vec3(-1, 0, 0)]),
    ("S",        ["walk", vec3(-1, 0, 0)],      ["walk", vec3(1, 0, 0)]),
    ("A",        ["walk", vec3(0, 1, 0)],       ["walk", vec3(0, -1, 0)]),
    ("D",        ["walk", vec3(0, -1, 0)],      ["walk", vec3(0, 1, 0)]),
    ("P",        ["toggle", "pause"],           None),
    ("SPACE",    ["jump", True],                ["jump", False]),
    ("F2",       ["toggle", "wireframe"],       None),
    ("F3",       ["toggle", "backface"],        None),
    ("F4",       ["toggle", "40fps"],           None),
]

# Turn a key name (like those above) into the number codes used by
# glfw. GLFW doesn't give us a function to do this, so we have to
# poke about a bit.
def key_code (name):
    symbol = "KEY_" + name
    return glfw.__dict__[symbol]

# This class handles all the input. Currently this is only keyboard
# input, so it looks up the key and decides what to do.
class InputHandler:
    __slots__ = [
        # Our app
        "app",
        # The dict of commands we understand
        "commands",
        # Our current keybindings
        "keys",
    ]

    def __init__ (self, app):
        self.app = app
        self.__init_commands()
        self.__init_keys()

    # This sets up .commands, which maps command names to the functions
    # we should call. For now this is a static dict.
    def __init_commands (self):
        app = self.app
        self.commands = {
            "jump":     app.player.jump,
            "pan":      app.camera.pan,
            "quit":     app.post_quit,
            "toggle":   app.options.toggle,
            "walk":     app.player.walk,
        }

    # This sets up .keys, which is a dict defining what the keys do.
    # Each keycode maps to a 2-element tuple; the first says what to do
    # on keydown, the second what to do on keyup. The names are looked
    # up as functions in .commands.
    # For now we build this from a static list. Later we want to read it
    # from a file.
    def __init_keys (self):
        self.keys = {}
        for b in _KEYS:
            k = key_code(b[0])
            self.keys[k] = (b[1], b[2])

    def handle_key (self, k, action):
        # If the keycode is not in our dict, we have nothing to do.
        if (k not in self.keys):
            return

        # Find the entry for the keycode, and choose the first part for
        # keydown and the second for keyup. If we have None then there
        # is nothing to do.
        bindings = self.keys[k]
        if action == glfw.PRESS:
            binding = bindings[0]
        elif action == glfw.RELEASE:
            binding = bindings[1]
        else:
            binding = None

        if binding is None:
            return

        # The first entry in the list is the command name, the rest are the
        # arguments for the command.
        name    = binding[0]
        args    = binding[1:]

        # Find the function by looking up in the Commands dict.
        function    = self.commands[name]
        # Call the function, passing the arguments. The * passes the
        # pieces of the list separately, rather than passing the whole list.
        function(*args)

# input.py - Handle user input

from    pygame.locals   import *

from    .       import options
from    .       import player

# This dict defines all the commands we can bind to keys.
# It is filled in by input_init because otherwise these functions might
# not exist yet.
Commands = {}

# This defines what all the keys do. Each keycode maps to a 2-element tuple;
# the first says what to do on keydown, the second what to do on keyup.
# The names are looked up as functions in Commands.
Key_Bindings = {
    K_ESCAPE:   (["quit"],                      None),
    K_q:        (["quit"],                      None),
    K_i:        (["pan", [0, 1]],               ["pan", [0, -1]]),
    K_k:        (["pan", [0, -1]],              ["pan", [0, 1]]),
    K_j:        (["pan", [-1, 0]],              ["pan", [1, 0]]),
    K_l:        (["pan", [1, 0]],               ["pan", [-1, 0]]),
    K_w:        (["walk", [1, 0, 0]],           ["walk", [-1, 0, 0]]),
    K_s:        (["walk", [-1, 0, 0]],          ["walk", [1, 0, 0]]),
    K_a:        (["walk", [0, 1, 0]],           ["walk", [0, -1, 0]]),
    K_d:        (["walk", [0, -1, 0]],          ["walk", [0, 1, 0]]),
    K_p:        (["toggle", "pause"],           None),
    K_SPACE:    (["jump", True],                None),
    K_F2:       (["toggle", "wireframe"],       None),
    K_F3:       (["toggle", "backface"],        None),
    K_F4:       (["toggle", "40fps"],           None),
}

def input_init (app):
    global Commands

    Commands = {
        "jump":     app.player.set_jump,
        "pan":      app.camera.pan,
        "quit":     app.post_quit,
        "toggle":   options.toggle,
        "walk":     app.player.set_walk,
    }

def input_handle_key (k, down):
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

    # The first entry in the list is the command name, the rest are the
    # arguments for the command.
    name    = binding[0]
    args    = binding[1:]

    # Find the function by looking up in the Commands dict.
    function    = Commands[name]
    # Call the function, passing the arguments. The * passes the
    # pieces of the list separately, rather than passing the whole list.
    function(*args)

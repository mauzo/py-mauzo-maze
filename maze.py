
# maze.py
# Playing with OpenGL

import OpenGL
OpenGL.ERROR_CHECKING = False

from OpenGL.GL      import *
from OpenGL.GLU     import *
import pygame
from pygame.locals  import *

from mauzo.maze.all import *

# Main

def main():
    my_app = app.init()

    # Open the window and setup pygame
    init_display()

    # This try: block catches errors and makes sure the finally: block
    # runs even if there's an error. Otherwise the window doesn't go away.
    try:
        # Run the other initialisation
        gl.init()
        text.init()
        input_init()
        init_world()
        init_player()
        camera_init()
        my_app.render.init()

        # Go into the main loop, which doesn't return until we quit the game.
        my_app.run()
    finally:
        display_quit()

main()

# walls
# Jump through platforms
# hold a direction
#looking up and down

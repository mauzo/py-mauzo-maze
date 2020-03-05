
# maze.py
# Playing with OpenGL

from OpenGL.GL      import *
from OpenGL.GLU     import *
import pygame
from pygame.locals  import *

from mauzo.maze.all import *


# Data

# Main

def main():
    # Open the window and setup pygame
    init_display()

    # This try: block catches errors and makes sure the finally: block
    # runs even if there's an error. Otherwise the window doesn't go away.
    try:
        # Run the other initialisation
        init_opengl()
        input_init()
        init_world()
        init_player()
        camera_init()

        # Go into the main loop, which doesn't return until we quit the game.
        mainloop()
    finally:
        display_quit()

main()

# walls
# Jump through platforms
# hold a direction
#looking up and down

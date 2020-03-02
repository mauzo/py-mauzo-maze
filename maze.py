
# maze.py
# Playing with OpenGL

from OpenGL.GL      import *
from OpenGL.GLU     import *
import pygame
from pygame.locals  import *

# I have started moving pieces into their own files.
from mauzo.maze.camera      import *
from mauzo.maze.display     import *
from mauzo.maze.drawing     import *
from mauzo.maze.events      import *
from mauzo.maze.input       import *
from mauzo.maze.options     import *
from mauzo.maze.player      import *
from mauzo.maze.render      import *
from mauzo.maze.vectors     import *
from mauzo.maze.world       import *

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

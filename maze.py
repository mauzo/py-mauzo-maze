
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

# Events
# These functions manage things that happen while the program is running.

# Handle a key-up or key-down event. k is the keycode, down is True or False.
def handle_key(k, down):
    input_handle_key(k, down)

# Handle a window resize event
def handle_resize (w, h):
    print("RESIZE:", w, "x", h)
    display_set_viewport(w, h)

# This is the main loop that runs the whole game. We wait for events
# and handle them as we need to.
def mainloop():
    # Set up a clock to keep track of the framerate.
    clock   = pygame.time.Clock()    
    fps     = Display["fps"]
    
    while True:
        # Check for events and deal with them.
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                print("FPS: ", clock.get_fps())
                return

            elif event.type == KEYDOWN:
                handle_key(event.key, True)

            elif event.type == KEYUP:
                handle_key(event.key, False)
                
            elif event.type == VIDEORESIZE:
                handle_resize(event.w, event.h)

        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        render()
        display_flip()

        # Run the physics. Pass in the time taken since the last frame.
        player_physics(clock.get_time())
        camera_physics()

        # Wait if necessary so that we don't draw more frames per second
        # than we want. Any more is just wasting processor time.
        clock.tick(fps)

# Main

def main():
    # Open the window and setup pygame
    init_display()

    # This try: block catches errors and makes sure the finally: block
    # runs even if there's an error. Otherwise the window doesn't go away.
    try:
        # Run the other initialisation
        init_opengl()
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

# events.py - Run the event loop

import  pygame
from    pygame.event        import Event
from    pygame.locals       import *

from . import camera
from . import display
from . import input
from . import player
from . import render

# This dict maps an event type to a function for handling that event.
# The lambdas are little functions defined on the spot. 
Handlers = {
    KEYDOWN:        lambda e: input.input_handle_key(e.key, True),
    KEYUP:          lambda e: input.input_handle_key(e.key, False),
    VIDEORESIZE:    lambda e: display.display_set_viewport(e.w, e.h),
}

# This is the main loop that runs the whole game. We wait for events
# and handle them as we need to.
def mainloop():
    # Set up a clock to keep track of the framerate.
    clock   = pygame.time.Clock()    
    
    while True:
        # Check for events and deal with them.
        events = pygame.event.get()
        for event in events:
            # Quit is special because it needs the clock
            if event.type == QUIT:
                print("FPS: ", clock.get_fps())
                return

            if event.type in Handlers:
                h = Handlers[event.type]
                h(event)

        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        render.render()
        display.display_flip()

        # Run the physics. Pass in the time taken since the last frame.
        dt = clock.get_time() / 1000
        player.player_physics(dt)
        camera.camera_physics()

        # Wait if necessary so that we don't draw more frames per second
        # than we want. Any more is just wasting processor time.
        clock.tick(display.Display["fps"])

# Tell pygame we want to quit.
def event_post_quit ():
    pygame.event.post(Event(QUIT))


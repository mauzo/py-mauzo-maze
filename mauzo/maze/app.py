# events.py - Run the event loop

import  pygame
from    pygame.event        import Event
from    pygame.locals       import *

from . import camera
from . import display
from . import input
from . import options
from . import player
from . import render
from . import world

# Temporary global to hold the app pointer
_APP = None

class MazeApp:
    __slots__ = ["clock", "fps", "handlers", "render", "run_physics"]

    def __init__ (self):
        # This dict maps an event type to a function for handling that event.
        # The lambdas are little functions defined on the spot. 
        self.handlers = {
            KEYDOWN:        lambda e: input.input_handle_key(e.key, True),
            KEYUP:          lambda e: input.input_handle_key(e.key, False),
            VIDEORESIZE:    lambda e: display.display_set_viewport(e.w, e.h),
        }

        # We are not paused to start with
        self.run_physics    = True
        # We start at 80 fps
        self.fps            = 80
        # Set up a clock to keep track of the framerate.
        self.clock          = pygame.time.Clock()

    # This has to be separate from __init__ so it can be called at the
    # right time.
    def init (self):
        # Open the window and setup pygame
        display.init_display()

        # Create a rendering object
        self.render         = render.Renderer(self)

        # Run the other initialisation
        input.input_init()
        world.init_world()
        player.init_player()
        camera.camera_init()

    def quit (self):
        pygame.quit()

    def option (s, o):
        return options.Options[o]

    # This is the main loop that runs the whole game. We wait for events
    # and handle them as we need to.
    def run (self):
        while True:
            # Run the event loop once
            if self.run_loop():
                return

            # Wait if necessary so that we don't draw more frames per second
            # than we want. Any more is just wasting processor time.
            self.clock.tick(self.fps)

    # Run the event loop once: handle any events, draw one frame to the
    # screen, and run the physics if we're not paused. Return True to
    # stop the app, False to continue.
    def run_loop (self):
        if self.process_events():
            return True
        self.render_frame()
        if self.run_physics:
            self.physics()
        return False

    # Process the event queue. Returns True to exit the event loop, False
    # to continue.
    def process_events (self):
        # Check for events and deal with them.
        events = pygame.event.get()
        for event in events:
            # Quit is special because it needs the clock
            if event.type == QUIT:
                print("FPS: ", self.clock.get_fps())
                return True

            if event.type in self.handlers:
                h = self.handlers[event.type]
                h(event)

        return False

    def render_frame (self):
        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        self.render.render()
        display.display_flip()

    def physics (self):
        # Run the physics. Pass in the time taken since the last frame.
        dt = self.clock.get_time() / 1000
        player.player_physics(dt)
        camera.camera_physics(dt)


def get_app ():
    global _APP
    if not _APP:
        _APP = MazeApp()
    return _APP

# Tell pygame we want to quit.
def event_post_quit ():
    pygame.event.post(Event(QUIT))

# events.py - Run the event loop

import  glfw

from . import camera
from . import display
from . import input
from . import options
from . import player
from . import render
from . import world

# Temporary global to hold the app pointer
_APP = None

class Clock:
    __slots__ = [
        "now",      # the time last time we updated
        "dt",       # the time difference last time we updated
        "paused",   # are we paused?
        "offset",   # our offset from 'real' time
    ]

    def __init__ (self):
        self.now    = 0
        self.dt     = 0
        self.offset = 0
        self.paused = None

    def update (self, real):
        if self.paused:
            return
        adjusted    = real - self.offset
        self.dt     = adjusted - self.now
        self.now    = adjusted

    def pause (self, now):
        self.paused = now

    def resume (self, now):
        self.offset += now - self.paused
        self.paused = None

class MazeApp:
    # This defines the attributes this object can have.
    __slots__ = [
        "camera",       # An object representing the camera
        "clock",        # A clock to keep track of the framerate
        "display",      # Our display
        "input",        # An object to handle input
        "options",      # Options the user can change
        "player",       # The player object
        "render",       # An object that knows how to draw a frame
        "run_physics",  # Should we run the physics?
        "world",        # Our World object, representing the current level
    ]

    # This is called automatically when we create a new object, to set
    # things up.
    def __init__ (self):
        # We are not paused to start with
        self.run_physics    = True
        # Set up a clock to keep track of the framerate.
        self.clock          = Clock()

        # Create objects representing other parts of the system
        self.options        = options.Options(self)
        self.display        = display.Display(self)
        self.world          = world.World(self)
        self.player         = player.Player(self)
        self.camera         = camera.Camera(self, self.player)
        self.render         = render.Renderer(self)

        # This must be last as it needs to get at the others (for now)
        self.input          = input.InputHandler(self)

    # This has to be separate from __init__ so it can be called at the
    # right time.
    def init (self):
        # Start up GLFW and open window
        self.init_glfw()
        self.display.init()
        self.init_handlers()

        # Run the other initialisation
        self.render.init()
        self.world.init()
        self.player.init()
        self.camera.init()

    def init_glfw (self):
        if not glfw.init():
            raise RuntimeError("Failed to init GLFW")
        glfw.set_error_callback(self.handle_glfw_error)

    def init_handlers (self):
        win = self.display.window

        glfw.set_framebuffer_size_callback(win,
            lambda win, w, h: self.display.set_viewport(w, h))
        glfw.set_key_callback(win,
            lambda win, key, code, action, mods: \
                self.input.handle_key(key, action))
        #glfw.set_cursor_pos_callback(window, self.handle_mouse_pos)
        #glfw.set_mouse_button_callback(window, self.handle_mouse_click)

    def handle_glfw_error (self, code, msg):
        raise RuntimeError("GLFW error %d: %s" % (code, msg))

    def quit (self):
        self.display.quit()
        glfw.terminate()

    def option (s, o):
        return s.options.get(o)

    # This is the main loop that runs the whole game. We wait for events
    # and handle them as we need to.
    def run (self):
        while not self.display.should_close():
            now     = glfw.get_time()
            self.clock.update(now)

            glfw.poll_events()
            self.render_frame()
            if self.run_physics:
                self.physics()

    def render_frame (self):
        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        self.render.render()
        self.display.flip()

    # Return the time now, in seconds.
    def now (self):
        return self.clock.now

    def physics (self):
        # Run the physics. Pass in the time taken since the last frame.
        dt = self.clock.dt
        self.player.physics(dt)
        self.camera.physics(dt)

    def post_quit (self):
        self.display.post_close()

    # The player has died...
    def die (self):
        print("AAAARGH!!!")
        self.player.reset()

    # The player has won...
    def win (self):
        print("YaaaY!!!!")
        self.post_quit()

def get_app ():
    global _APP
    if not _APP:
        _APP = MazeApp()
    return _APP


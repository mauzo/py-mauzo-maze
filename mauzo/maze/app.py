# events.py - Run the event loop

import  glfw

from . import camera
from . import display
from . import exceptions
from . import input
from . import options
from . import player
from . import render
from . import world

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
        "argv",         # Our command-line arguments
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
    def __init__ (self, argv):
        self.argv           = argv

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
        self.init_options()

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

    def init_options (self):
        opt = self.options

        opt.register("pause", on=self.pause_on, off=self.pause_off)

    def handle_glfw_error (self, code, msg):
        raise RuntimeError("GLFW error %d: %s" % (code, msg))

    def quit (self):
        self.display.quit()
        glfw.terminate()

    def option (s, o):
        return s.options.get(o)

    def pause_on (self):
        self.run_physics = False

    def pause_off (self):
        self.run_physics = True

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
        ctx = self.clock

        try:
            self.player.update(ctx)
            self.camera.physics(ctx)
            self.world.physics(ctx)
        except exceptions.XMaze as x:
            x.handle(self)

    def post_quit (self):
        self.display.post_close()

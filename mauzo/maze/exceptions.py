# exceptions.py - our exception classes

# The base class for our exceptions
class XMaze (Exception):
    def handle (self, app):
        raise RuntimeError("attempt to .handle XMaze")

# The player has died
class XDie (XMaze):
    def handle (self, app):
        print("AAAARGH!!!")
        app.player.reset()
        app.camera.reset()
        app.world.reset()

# The player has activated a portal
class XPortal (XMaze):
    __slots__ = [
        "to",       # where to port to
    ]

    def __init__ (self, to):
        self.to = to

    def handle (self, app):
        print("YaaaY!!!!")
        if self.to:
            app.world.load_level(self.to)
            app.player.reset()
            app.camera.reset()
        else:
            app.post_quit()

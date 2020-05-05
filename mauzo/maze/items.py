# items.py - Item class definitions

from    OpenGL.GL       import *

from    .               import  drawing as dr
from    .exceptions     import  *
from    .geometry       import  *
from    .               import  gl

class Item:
    __slots__ = [
        "world",    # the world we are in
        "pos",      # our position
    ]

    bump    = 0.5

    # We accept a 'type' argument and do nothing with it.
    def __init__ (self, world, pos, type=None):
        self.world  = world
        self.pos    = vec3(pos)

    def render (self, ctx):
        raise RuntimeError("render called on base Item")

    def activate (self, player):
        raise RuntimeError("activate called on base Item")

    def collide (self, pos, bump):
        d   = glm.length(self.pos - pos)
        b   = bump + self.bump
        return d < b

    def reset (self):
        pass

class ModelItem (Item):
    __slots__ = [
        "model",    # Our model
    ]

    def __init__ (self, **kws):
        super().__init__(**kws) 

        render       = self.world.app.render
        self.model   = render.load_model(self.model_name)

    def model_matrix (self, ctx):
        return glm.translate(mat4(1), self.pos)

    def render (self, ctx):
        prg     = ctx.shader
        model   = self.model_matrix(ctx)
        normal  = gl.make_normal_matrix(model)

        prg.use()
        prg.u_model(model)
        prg.u_normal_matrix(normal)
        self.model.render(prg)

class Key (ModelItem):
    __slots__ = [
        "visible",  # Can you  see it?
    ]

    model_name  = "key"

    def __init__ (self, **kws):
        # Call up to the parent class __init__
        super().__init__(**kws)

        self.reset()

    def reset (self):
        super().reset()
        self.visible = True  

    def model_matrix (self, ctx):
        model   = super().model_matrix(ctx)
        model   = glm.rotate(model, 0.8 * PI * ctx.now, Zpos)
        model   = glm.rotate(model, PI/3, Ypos)
        return model

    def render (self, ctx):
        if self.visible:
            super().render(ctx)

    def activate (self, player):
        if self.visible:
            player.have_key = True
            self.visible = False

class Portal (ModelItem):
    __slots__ = [
        "to",           # The level to port to
        "angle",        # The angle the portal is facing
    ]

    model_name  = "portal"

    def __init__ (self, angle, to=None, **kws):
        # Call up to the parent's __init__
        super().__init__(**kws)

        # Now do our own stuff
        self.to     = to
        self.angle  = angle * PI

    def activate (self, player):
        print("PORT TO", self.to)
        raise XPortal(self.to)

    def model_matrix (self, ctx):
        model   = super().model_matrix(ctx)
        model   = glm.rotate(model, self.angle, Zpos)
        return model

    def collide (self, pos, bump):
        if super().collide(pos, bump) == False:
            return False
        return True
        
            

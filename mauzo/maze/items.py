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

    def update (self, ctx):
        pass

class ModelItem (Item):
    __slots__ = [
        "model",            # Our model
        "model_matrix",     # Our model matrix
        "inverse_matrix",   # The inverse of model_matrix
        "normal_matrix",    # The matrix to use for mormals
    ]

    def __init__ (self, **kws):
        super().__init__(**kws) 

        render       = self.world.app.render
        self.model   = render.load_model(self.model_name)

        self.set_model_matrix(glm.translate(Id4, self.pos))

    def set_model_matrix (self, model):
        self.model_matrix       = model
        self.inverse_matrix     = glm.inverse(model)
        self.normal_matrix      = gl.make_normal_matrix(model)

    def render (self, ctx):
        prg     = ctx.shader
        model   = self.model_matrix
        normal  = self.normal_matrix

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

    def update (self, ctx):
        super().update(ctx)

        model   = glm.translate(Id4, self.pos)
        model   = glm.rotate(model, 0.8 * PI * ctx.now, Zpos)
        model   = glm.rotate(model, PI/3, Ypos)

        self.set_model_matrix(model)

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

        model   = glm.translate(Id4, self.pos)
        model   = glm.rotate(model, self.angle, Zpos)
        self.set_model_matrix(model)

    def activate (self, player):
        print("PORT TO", self.to)
        raise XPortal(self.to)

    def collide (self, pos, bump):
        if super().collide(pos, bump) == False:
            return False
        return True

class LockedDoor (ModelItem):
    __slots__ = [
        "to",           # The level to port to
        "angle",        # The angle the portal is facing
        "unlock",       # When you unlock the portal
    ]

    model_name  = "lock_portal"

    def __init__ (self, angle, to=None, **kws):
        # Call up to the parent's __init__
        super().__init__(**kws)

        # Now do our own stuff
        self.to     = to
        self.angle  = angle * PI
        self.unlock = True

        model   = glm.translate(Id4, self.pos)
        model   = glm.rotate(model, self.angle, Zpos)
        self.set_model_matrix(model)

    def activate (self, player):
        if self.unlock == True:
            print("PORT TO", self.to)
            raise XPortal(self.to)
        else:
            print("The door is locked")
            

    def collide (self, pos, bump):
        if super().collide(pos, bump) == False:
            return False
        return True
        
        
class Spike (ModelItem):
    __slots__ = [
        "angle",        # The angle the spike is facing
        "size",         # How large it is 
    ]

    model_name  = "spike"

    def __init__ (self, angle, size, **kws):
        # Call up to the parent's __init__
        super().__init__(**kws)

        # Now do our own stuff
        self.angle  = angle * PI
        self.size   = size  * 2

        model   = glm.translate(Id4, self.pos)
        model   = glm.rotate(model, self.angle, Zpos)
        model   = glm.scale(model, vec3(self.size))
        self.set_model_matrix(model)
        
    def activate (self, player):
        player.set_damage()

    def collide (self, opos, bump):
        pos = self.inverse_matrix * vec4(opos, 1)
        if pos.x < 1 and pos.x > -1 \
           and pos.y < 1 and pos.y > -1 \
           and pos.z > 0 and pos.z < 0.3:
            print("SPIKE:", opos, pos)
            return True
        return False

class Heart (ModelItem):
    model_name = "heart"

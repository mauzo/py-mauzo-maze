# items.py - Item class definitions

from    OpenGL.GL       import *

from    .               import  drawing as dr
from    .exceptions     import  *
from    .geometry       import  *
from    .               import  gl

PI = glm.pi()

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

class Key (Item):
    __slots__ = [
        "model",    # our model
        "visible",  # Can you  see it?
    ]

    def __init__ (self, **kws):
        # Call up to the parent class __init__
        super().__init__(**kws)

        # Now do our own stuff
        render       = self.world.app.render
        self.model   = render.load_model("key")

        self.reset()

    def reset (self):
        super().reset()
        self.visible = True  

    def render (self, ctx):
        if not self.visible:
            return

        prg     = ctx.shader
        now     = ctx.now
        model   = glm.translate(mat4(1), self.pos)
        model   = glm.scale(model, vec3(0.2))
        model   = glm.rotate(model, 0.8 * PI * now, vec3(0, 0, 1))
        model   = glm.rotate(model, PI/3, vec3(0, 1, 0))
        normal  = gl.make_normal_matrix(model)

        prg.use()
        prg.u_model(model)
        prg.u_normal_matrix(normal)
        self.model.render(prg)

    def activate (self, player):
        if self.visible:
            player.have_key = True
            self.visible = False

class Portal (Item):
    __slots__ = [
        "vao",          # A VAO to draw a box
        "to",           # The level to port to
    ]

    def __init__ (self, to, **kws):
        # Call up to the parent's __init__
        super().__init__(**kws)

        # Now do our own stuff
        self.to     = to

        buf         = dr.make_ppiped(vec3(-0.5, -0.5, -0.5),
                        vec3(1, 0, 0), vec3(0, 0, 1), vec3(0, 1, 0))
        vbo         = gl.Buffer("vbo", buf)
        vao         = gl.VAO()
        attrs       = gl.shader_attribs()

        vbo.bind()
        vao.bind()
        vao.add_attrib(attrs["b_pos"],      3, 6, 0)
        vao.add_attrib(attrs["b_normal"],   3, 6, 3)
        vao.add_primitive(GL_TRIANGLES, 0, 36)
        vao.unbind()

        self.vao    = vao

    def render (self, ctx):
        prg     = ctx.shader
        model   = glm.translate(mat4(1), self.pos)
        model   = glm.scale(model, vec3(0.8))
        normal  = gl.make_normal_matrix(model)

        prg.use()
        prg.u_model(model)
        prg.u_normal_matrix(normal)
        prg.u_material_diffuse(vec3(1, 1, 1))
        prg.u_material_specular(1)
        prg.u_material_shininess(128)

        self.vao.use()
        self.vao.render()

    def activate (self, player):
        print("PORT TO", self.to)
        raise XPortal(self.to)


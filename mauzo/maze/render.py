# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

import  glm
from    glm         import mat3, mat4, vec3, vec4
from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import gl
from    .           import model
from    .           import text

class Renderer:
    __slots__ = [
        "app",          # our app
        "models",       # models we have loaded
        "overlay",      # the text overlay
        "shader",       # a shader program
    ]

    def __init__ (self, app):
        self.app        = app
        self.models     = {}
        self.overlay    = text.Overlay(app)

    def init (self):
        gl.init()
        self.overlay.init()
        self.init_shader()

    def init_shader (self):
        slc     = gl.ShaderCompiler()
        shader  = slc.build_shader(vert="plain", frag="maze")
        slc.delete()

        self.shader = shader

    def load_model (self, name):
        if name in self.models:
            return self.models[name]

        m   = model.Model("model/%s/%s.obj" % (name, name))
        m.make_vaos(self.shader)

        return m

    # This is called to render every frame. We clear the window, position the
    # camera, and then call the display list to draw the world.
    def render (self):
        app     = self.app
        world   = app.world
        proj    = app.display.projection
        view    = app.camera.view_matrix()
        prg     = self.shader

        gl.clear()

        gl.use_ffp()
        gl.load_ffp_matrix(view)
        app.world.render()
        app.player.render()
        self.overlay.render()

        prg.use()
        prg.u_proj(proj)
        prg.u_view(view)
        prg.u_view_pos(glm.inverse(view) * vec4(0, 0, 0, 1))
        world.render_keys(prg)

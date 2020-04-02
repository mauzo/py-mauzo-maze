# render.py - Render
# These functions actually draw every frame. Most of the drawing
# has already been done and put in the display lists.

import  glm
from    glm         import mat3, mat4, vec3, vec4
from    OpenGL.GL   import *
from    OpenGL.GLU  import *

from    .           import gl
from    .           import model
from    .           import overlay

class RenderContext:
    __slots__ = [
        "now",          # the time now
        "shader",       # the shader program we are using
    ]


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
        self.overlay    = overlay.Overlay(app)

    def init (self):
        gl.init()
        self.overlay.init()
        self.init_shader()
        self.register_options()

    def init_shader (self):
        slc     = gl.ShaderCompiler()
        shader  = slc.build_shader(vert="plain", frag="maze")
        slc.delete()

        self.shader = shader

    def wireframe_on (self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def wireframe_off (self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def backface_on (self):
        glDisable(GL_CULL_FACE)
        # Display back faces bright cyan
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1)
        glMaterialfv(GL_BACK, GL_EMISSION, [0, 1, 1])

    def backface_off (self):
        glEnable(GL_CULL_FACE)

    def register_options (self):
        opt     = self.app.options

        opt.register("wireframe",
            on=self.wireframe_on, off=self.wireframe_off)
        opt.register("backface",
            on=self.backface_on, off=self.backface_off)

    def load_model (self, name):
        if name in self.models:
            return self.models[name]

        m = model.Model("model/%s/%s.obj" % (name, name))
        self.models[name] = m

        return m

    # This is called to render every frame. We clear the window, position the
    # camera, and then call the display list to draw the world.
    def render (self):
        app     = self.app
        world   = app.world
        proj    = app.display.perspective
        view    = app.camera.view_matrix()
        prg     = self.shader

        ctx         = RenderContext()
        ctx.shader  = prg
        ctx.now     = app.now()

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
        world.render_items(ctx)

        self.overlay.render_gl3(ctx)

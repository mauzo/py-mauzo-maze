# overlay.py - the HUD overlay

import  glm
from    glm             import mat3, mat4, vec3, vec4
import  numpy           as np
from    OpenGL.GL       import *

from    .       import gl
from    .       import text

vertices = np.array([
    0, 0, 0,
    500, 0, 0,
    250, 500, 0,
], dtype=GLfloat)

class Overlay:
    __slots__ = [
        "app",      # our app
        "display",  # our display
        "font",     # our font
        "key",      # the key model
        "shader",   # our shader program
        "vao",
    ]

    def __init__ (self, app):
        self.app        = app
        self.display    = app.display

    def init (self):
        text.init()
        self.font   = text.GLFont("stencil.ttf", 100)
        self.key    = self.app.render.load_model("key")

        vbo     = gl.Buffer("vbo", vertices)
        vao     = gl.VAO()

        vbo.bind()
        vao.add_attrib(0,   3, 3, 0)
        vbo.unbind()
        vao.add_primitive(GL_TRIANGLES, 0, 3)
        vao.unbind()

        self.vao    = vao
        
        slc     = gl.ShaderCompiler()
        prg     = slc.build_shader(vert="plain", frag="overlay")
        slc.delete()

        self.shader = prg
        prg.use()
        prg.u_view(mat4(1))
        prg.u_normal_matrix(mat3(1))
        gl.use_ffp()

    # Push new GL state suitable for rendering text.
    def push_gl_state (self):
        ortho   = self.display.overlay

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        gl.load_ffp_matrix(ortho)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glPushAttrib(GL_ENABLE_BIT|GL_TEXTURE_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND)

    # Draw the text
    def render (self):
        prg = self.app.render.shader
        key = self.key
        vao = self.vao
        prj = self.display.overlay

        self.push_gl_state()

        if self.app.option("pause"):
            glColor4f(1, 0.5, 0, 0.8)
            self.font.show("PAUSED", 0, 0, 100)

        self.pop_gl_state()

        mod = glm.translate(mat4(1), vec3(50, 50, 0))
        mod = glm.scale(mod, vec3(0.1, 0.1, 0.1))
        prg.use()
        prg.u_proj(self.display.perspective)
        prg.u_model(mat4(1))
        #key.render(prg)
        vao.use()
        vao.render()

    # Pop the state pushed above.
    def pop_gl_state (self):
        glPopAttrib()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


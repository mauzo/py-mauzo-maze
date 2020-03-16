from    math            import sin, cos
import  numpy           as np
import  signal

import  pygame
from    pygame.locals   import *

import  glm
from    glm             import vec3, vec4, mat4, radians
# Do this last, since pygame.locals conflicts
from    OpenGL.GL       import *

import  mauzo.maze.gl               as gl
import  mauzo.learnopengl.camera    as logcam

WINSIZE = (500, 500)

def flip ():
    pygame.display.flip()

def sigint (x, y):
    raise KeyboardInterrupt()

def init ():
    signal.signal(signal.SIGINT, sigint)
    pygame.init()
    pygame.display.set_mode(WINSIZE, OPENGL|DOUBLEBUF|RESIZABLE)

    # depth
    glEnable(GL_DEPTH_TEST)
    # blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Pixel transfer
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

def run (app):
    clock   = pygame.time.Clock()
    mouseok = False

    def set_mouseok (b):
        nonlocal mouseok # grr stupid language
        mouseok = b
        pygame.mouse.set_visible(not b)
        pygame.event.set_grab(b)

    while True:
        es = pygame.event.get()
        for e in es:
            if e.type == QUIT:
                return
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                set_mouseok(False)
            if e.type == MOUSEBUTTONDOWN:
                set_mouseok(True)
            if e.type == MOUSEMOTION and mouseok:
                app.mouse(e)
            if e.type == VIDEORESIZE:
                glViewport(0, 0, e.w, e.h)
                app.resize(e.w, e.h)

        dt = clock.get_time() / 1000

        app.update(dt)
        app.render()
        clock.tick(80)

vertices = np.array([
    # position         # normal          # texture
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
     0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,

    -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,
     0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 0.0,
     0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
     0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,

    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 1.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0, 0.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,

     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
], dtype=GLfloat)

indices = np.array([
    0, 1, 3,
    1, 2, 3,
], dtype=GLint)

cube_positions = [
    vec3(0, 0, 0),
    vec3(2, 5, -15),
    vec3(-1.5, -2.2, -2.5),
    vec3(-3.8, -2.0, -12.3),
    vec3(2.4, -0.4, -3.5),
    vec3(-1.7, 3.0, -7.5),
    vec3(1.3, -2.0, -2.5),
    vec3(1.5, 2.0, -2.5),
    vec3(1.5, 0.2, -1.5),
    vec3(-1.3, 1.0, -1.5),
]

def read_glsl(name):
    with open("glsl/" + name + ".glsl", "rb") as f:
        return f.read()

def make_shader (vertex="vertex", fragment="frag"):
    prg = gl.Shader()
    prg.add_shader("vertex", read_glsl(vertex))
    prg.add_shader("fragment", read_glsl(fragment))
    prg.link()

    return prg

class App:
    def __init__ (self):
        self.resize(WINSIZE[0], WINSIZE[1])
        
    def setup_box_vao (self):
        prg     = make_shader("v-box", "f-box")
        vao     = gl.VAO(prg)

        vao.setup_attrib("b_pos",       3, 8, 0)
        vao.setup_attrib("b_normal",    3, 8, 3)
        vao.setup_attrib("b_tex",       2, 8, 6)
        vao.add_primitive(GL_TRIANGLES, 0, 36)
        vao.unbind()

        rgb     = gl.Texture()
        rgb.load_file(GL_RGB, "tex/container2rgb.tiff")
        spec    = gl.Texture()
        spec.load_file(GL_ALPHA, "tex/container2s.tiff")

        t = vao.add_texture(rgb)
        prg.set_uniform1i("u_material.diffuse", t)
        t = vao.add_texture(spec)
        prg.set_uniform1i("u_material.specular", t)
        prg.set_uniform1f("u_material.shininess",   32.0)

        prg.set_uniform3f("u_light.ambient",        0.2, 0.2, 0.2)
        prg.set_uniform3f("u_light.diffuse",        0.7, 0.7, 0.7)
        prg.set_uniform3f("u_light.specular",       1.0, 1.0, 1.0)

        self.box = vao

    def setup_lightcube_vao (self):
        prg     = make_shader("v-light", "f-light")
        vao     = gl.VAO(prg)

        prg.set_uniform3f("u_color", 1, 1, 1)

        vao.setup_attrib("b_pos",   3, 8, 0)
        vao.add_primitive(GL_TRIANGLES, 0, 36)
        vao.unbind()

        self.lightcube = vao

    def setup (self):
        glClearColor(0, 0, 0, 1.0)

        vbo     = gl.Buffer("vbo", vertices)

        self.light_pos  = vec3(1.2, 1.0, 2.0)

        vbo.bind()
        self.setup_box_vao()
        self.setup_lightcube_vao()
        vbo.unbind()

        self.camera     = logcam.Camera(vec3(1, 0, 6))

    def resize (self, w, h):
        self.width  = w
        self.height = h
        self.aspect = w/h

    def mouse (self, e):
        self.camera.process_mouse(e.rel[0], -e.rel[1])

    def update (self, dt):
        camera  = self.camera
        keys    = pygame.key.get_pressed()
        now     = pygame.time.get_ticks()/1000

        prg     = self.box.shader

        self.light_pos  = vec3(1 + sin(now) * 2, sin(now/2), 2)
        prg.set_uniform3v("u_light.position", self.light_pos)

#        color   = vec3(sin(now * 2), sin(now * 0.7), sin(now * 1.3))
#        prg.set_uniform3v("u_light.ambient",    color * 0.5)
#        prg.set_uniform3v("u_light.diffuse",    color * 0.2)
#        self.lightcube.shader.set_uniform3v("u_color", color)

        if keys[K_q]:
            camera.process_keyboard(logcam.BACKWARD, dt)
        if keys[K_e]:
            camera.process_keyboard(logcam.FORWARD, dt)
        if keys[K_w]:
            camera.process_keyboard(logcam.UP, dt)
        if keys[K_s]:
            camera.process_keyboard(logcam.DOWN, dt)
        if keys[K_a]:
            camera.process_keyboard(logcam.LEFT, dt)
        if keys[K_d]:
            camera.process_keyboard(logcam.RIGHT, dt)

    def render (self):

        camera  = self.camera

        proj    = glm.perspective(radians(camera.zoom), self.aspect, 0.1, 100)
        view    = camera.get_view_matrix()

        for vao in self.box, self.lightcube:
            vao.set_matrix4("u_proj", proj)
            vao.set_matrix4("u_view", view)

        gl.clear()

        model   = mat4(1)
        model   = glm.translate(model, self.light_pos)
        model   = glm.scale(model, vec3(0.2))
        self.lightcube.set_matrix4("u_model", model)
        self.lightcube.use()
        self.lightcube.render()

        model   = mat4(1)
        normal  = gl.make_normal_matrix(model)
        self.box.set_matrix4("u_model",              model)
        #self.box.set_matrix3("u_normal_matrix",      normal)
        self.box.shader.set_uniform3v("u_view_pos", camera.position)
        self.box.use()
        self.box.render()

        flip()

init()
app = App()
app.setup()
run(app)

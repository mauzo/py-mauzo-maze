from    math            import sin, cos
import  numpy           as np
import  signal

import  pygame
from    pygame.locals   import *

import  glm
from    glm             import vec3, vec4, mat4, radians
# Do this last, since pygame.locals conflicts
from    OpenGL.GL       import *
import  pywavefront

import  mauzo.maze.gl               as gl
import  mauzo.learnopengl.camera    as logcam
import  mauzo.maze.model            as model

WINSIZE = (500, 500)

def flip ():
    pygame.display.flip()

def sigint (x, y):
    raise KeyboardInterrupt()

def init ():
    signal.signal(signal.SIGINT, sigint)
    pygame.init()
    pygame.display.set_mode(WINSIZE, OPENGL|DOUBLEBUF|RESIZABLE)

    # depth/cull
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
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
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,

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
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
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

light_positions = [
    vec3(0.7, 0.2, 2.0),
    vec3(2.3, -3.3, 4.0),
    vec3(-4.0, 2.0, -12.0),
    vec3(0.0, 0.0, -3.0),
]

light_colors = [
    vec3(0.8, 0.8, 0.8),
    vec3(0.8, 0.8, 0.8),
    vec3(0.8, 0.8, 0.8),
    vec3(0.8, 0.8, 0.8),
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
        
    def setup_shader (self, slc):
        prg         = slc.build_shader(["v-box"], ["f-box"])
        self.shader = prg
        
        prg.use()

        prg.u_sun_direction(vec3(-0.2, -1.0, -0.3))
        prg.u_sun_color_ambient(vec3(0.05, 0.05, 0.05))
        prg.u_sun_color_diffuse(vec3(0.4, 0.4, 0.4))
        prg.u_sun_color_specular(vec3(0.5, 0.5, 0.5))

        prg.u_light0_position(light_positions[0])
        prg.u_light0_color_ambient(light_colors[0]/16)
        prg.u_light0_color_diffuse(light_colors[0])
        prg.u_light0_color_specular(vec3(1.0, 1.0, 1.0))
        prg.u_light0_linear(0.09)
        prg.u_light0_quadratic(0.032)
        prg.u_light1_position(light_positions[1])
        prg.u_light1_color_ambient(light_colors[1]/16)
        prg.u_light1_color_diffuse(light_colors[1])
        prg.u_light1_color_specular(vec3(1.0, 1.0, 1.0))
        prg.u_light1_linear(0.09)
        prg.u_light1_quadratic(0.032)
        prg.u_light2_position(light_positions[2])
        prg.u_light2_color_ambient(light_colors[2]/16)
        prg.u_light2_color_diffuse(light_colors[2])
        prg.u_light2_color_specular(vec3(1.0, 1.0, 1.0))
        prg.u_light2_linear(0.09)
        prg.u_light2_quadratic(0.032)
        prg.u_light3_position(light_positions[3])
        prg.u_light3_color_ambient(light_colors[3]/16)
        prg.u_light3_color_diffuse(light_colors[3])
        prg.u_light3_color_specular(vec3(1.0, 1.0, 1.0))
        prg.u_light3_linear(0.09)
        prg.u_light3_quadratic(0.032)

        #cutoff      = cos(radians(8))
        #softness    = cos(radians(7)) - cutoff
        #prg.u_magic_cutoff(cutoff)
        #prg.u_magic_softness(softness)
        #prg.u_magic_limit(5.0)
#        prg.u_spot_cutoff(cutoff)
#        prg.u_spot_softness(softness)
#        prg.u_spot_color_ambient(vec3(0.05, 0.05, 0.05))
#        prg.u_spot_color_diffuse(vec3(0.9, 0.6, 0.6))
#        prg.u_spot_color_specular(vec3(1.0, 0.4, 1.0))
        #prg.u_spot_linear(0.045)
        #prg.u_spot_quadratic(0.0075)

    def setup_model (self):
        obj         = pywavefront.Wavefront("model/nanosuit/nanosuit.obj")
        box         = model.Mesh(obj.mesh_list[2])
        self.model  = box

        box.make_vao(self.shader)

    def setup_lightcube_vao (self, slc):
        prg     = slc.build_shader(["v-light"], ["f-light"])
        vao     = gl.VAO(prg)
        vbo     = gl.Buffer("vbo", vertices)

        vbo.bind()
        vao.bind()
        vao.add_attrib(prg.b_pos, 3, 8, 0)
        vao.add_primitive(GL_TRIANGLES, 0, 36)
        vao.unbind()
        vbo.unbind()

        self.lightcube      = vao

    def setup (self):
        glClearColor(1, 1, 1, 1.0)

        self.light_pos  = vec3(1.2, 1, 2)

        slc     = gl.ShaderCompiler()

        self.setup_shader(slc)
        self.setup_model()
        self.setup_lightcube_vao(slc)

        slc.delete()

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

        gl.clear()

        vao     = self.lightcube
        prg     = vao.shader
        prg.use()
        prg.u_proj(proj)
        prg.u_view(view)
        vao.use()
        for i in range(4):
            model   = mat4(1)
            model   = glm.translate(model, light_positions[i])
            model   = glm.scale(model, vec3(0.2))
            prg.u_model(model)
            prg.u_color(light_colors[i])
            vao.render()

        mod     = self.model
        prg     = self.shader
        prg.use()
        prg.u_proj(proj)
        prg.u_view(view)
        prg.u_view_pos(camera.position)
        mod.use(prg)
        for i in range(len(cube_positions)):
            model   = mat4(1)
            model   = glm.translate(model, cube_positions[i])
            model   = glm.rotate(model, radians(20*i), vec3(1, 0.3, 0.5))
            normal  = gl.make_normal_matrix(model)

            prg.u_model(model)
            prg.u_normal_matrix(normal)
            mod.render()

        flip()

init()
app = App()
app.setup()
run(app)

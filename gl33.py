from    math            import sin, cos
import  numpy           as np
import  signal

import  glfw
import  glm
from    glm             import vec3, vec4, mat4, radians
from    OpenGL.GL       import *
import  pywavefront

import  mauzo.maze.gl               as gl
import  mauzo.learnopengl.camera    as logcam
import  mauzo.maze.model            as model

WINSIZE = (500, 500)

def sigint (x, y):
    raise KeyboardInterrupt()

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
        self.mouseok    = False
        self.mouse_x    = 0
        self.mouse_y    = 0
        self.resize(WINSIZE[0], WINSIZE[1])

    def handle_glfw_error (self, code, msg):
        raise RuntimeError("glfw error: " + msg)
        
    def init (self):
        signal.signal(signal.SIGINT, sigint)
        if not glfw.init():
            raise RuntimeError("failed to init glfw")
        glfw.set_error_callback(self.handle_glfw_error)

        window = glfw.create_window(*WINSIZE, "GL3", None, None);
        if not window:
            raise RuntimeError("failed to create window")
        self.window = window
        glfw.make_context_current(window)

        glfw.swap_interval(1)
        glfw.set_framebuffer_size_callback(window, self.handle_resize)
        glfw.set_key_callback(window, self.handle_key)
        glfw.set_cursor_pos_callback(window, self.handle_mouse_pos)
        glfw.set_mouse_button_callback(window, self.handle_mouse_click)

    def delete (self):
        glfw.destroy_window(self.window)
        glfw.terminate()

    def set_mouseok (self, b):
        self.mouseok = b
        if b:
            glfw.set_input_mode(self.window, glfw.CURSOR, 
                glfw.CURSOR_DISABLED)
        else:
            glfw.set_input_mode(self.window, glfw.CURSOR,
                glfw.CURSOR_NORMAL)
            
    def handle_resize (self, window, w, h):
        glViewport(0, 0, w, h)
        self.resize(w, h)

    def resize (self, w, h):
        self.width  = w
        self.height = h
        self.aspect = w/h

    def handle_key (self, window, key, code, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            self.set_mouseok(False)

    def handle_mouse_pos (self, window, x, y):
        if self.mouseok:
            self.camera.process_mouse(x - self.mouse_x, self.mouse_y - y)
        self.mouse_x    = x
        self.mouse_y    = y

    def handle_mouse_click (self, window, button, action, mods):
        if action == glfw.PRESS:
            self.set_mouseok(True)

    def run (self):
        window  = self.window
        last    = glfw.get_time()
        while not glfw.window_should_close(window):
            glfw.poll_events()

            now     = glfw.get_time()
            dt      = now - last
            last    = now

            self.update(dt)
            self.render()
            glfw.swap_buffers(window)

    def setup_shader (self, slc):
        prg         = slc.build_shader(vert="plain", frag="material")
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
        key         = model.Model("model/nanosuit/nanosuit.obj")
        self.model  = key

        key.make_vaos(self.shader)

    def setup_lightcube_vao (self, slc):
        prg     = slc.build_shader(vert="plain", frag="color")
        vao     = gl.VAO(prg)
        vbo     = gl.Buffer("vbo", vertices)

        vbo.bind()
        vao.bind()
        vao.add_attrib(prg.b_pos, 3, 8, 0)
        vao.add_primitive(GL_TRIANGLES, 0, 36)
        vao.unbind()
        vbo.unbind()

        self.lightcube      = vao

    def setup_gl (self):
        # depth/cull
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        # blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # Pixel transfer
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        # clear
        glClearColor(1, 1, 1, 1.0)

    def setup (self):
        self.light_pos  = vec3(1.2, 1, 2)

        self.setup_gl()

        slc     = gl.ShaderCompiler()

        self.setup_shader(slc)
        self.setup_model()
        self.setup_lightcube_vao(slc)

        slc.delete()

        self.camera     = logcam.Camera(vec3(1, 0, 6))

    def update (self, dt):
        camera  = self.camera
        window  = self.window

        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            camera.process_keyboard(logcam.BACKWARD, dt)
        if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            camera.process_keyboard(logcam.FORWARD, dt)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            camera.process_keyboard(logcam.UP, dt)
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            camera.process_keyboard(logcam.DOWN, dt)
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            camera.process_keyboard(logcam.LEFT, dt)
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
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
        glDisable(GL_TEXTURE_2D)
        for i in range(len(cube_positions)):
            model   = mat4(1)
            model   = glm.translate(model, cube_positions[i])
            model   = glm.rotate(model, radians(20*i), vec3(1, 0.3, 0.5))
            normal  = gl.make_normal_matrix(model)

            prg.u_model(model)
            prg.u_normal_matrix(normal)
            mod.render(prg)


app = App()
app.init()
app.setup()
app.run()

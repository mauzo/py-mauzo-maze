import  math
import  numpy           as np
import  signal

import  pygame
from    pygame.locals   import *

import  glm
# Do this last, since pygame.locals conflicts
from    OpenGL.GL       import *

import  mauzo.maze.gl   as gl

WINSIZE = (500, 500)

def flip ():
    pygame.display.flip()

def sigint (x, y):
    raise KeyboardInterrupt()

def init ():
    signal.signal(signal.SIGINT, sigint)
    pygame.init()
    pygame.display.set_mode(WINSIZE, OPENGL|DOUBLEBUF)

    # blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Pixel transfer
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

def run (args):
    clock = pygame.time.Clock()
    while True:
        es = pygame.event.get()
        for e in es:
            if e.type == QUIT:
                return

        update(*args)
        render(*args)
        clock.tick(80)

vertices = np.array([
    [0.5, 0.5, 0,     1, 0, 0,      1, 1],
    [0.5, -0.5, 0,    0, 1, 0,      1, 0],
    [-0.5, -0.5, 0,   0, 0, 1,      0, 0],
    [-0.5, 0.5, 0,    1, 1, 0,      0, 1],
], dtype=GLfloat)

indices = np.array([
    0, 1, 3,
    1, 2, 3,
], dtype=GLint)

def read_glsl(name):
    with open("glsl/" + name + ".glsl", "rb") as f:
        return f.read()

def make_shader ():
    prg = gl.Shader()
    prg.add_shader("vertex", read_glsl("vertex"))
    prg.add_shader("fragment", read_glsl("frag"))
    prg.link()

    return prg

def setup ():
    glClearColor(0.2, 0.3, 0.3, 1.0)

    cont    = gl.Texture(linear=False)
    cont.load_file(GL_RGB, "tex/container.jpg")
    face    = gl.Texture(linear=False)
    face.load_file(GL_RGBA, "tex/face.png")

    prg     = make_shader()
    vbo     = gl.Buffer("vbo", vertices)
    ebo     = gl.Buffer("ebo", indices)
    vao     = gl.VAO(prg)

    vao.add_vbo(vbo)
    vao.setup_attrib("b_pos",   3, 8, 0)
    #vao.setup_attrib("b_color", 3, 8, 3)
    vao.setup_attrib("b_tex",   2, 8, 6)

    t = vao.add_texture(cont)
    prg.set_uniform1i("u_basetex", t)
    t = vao.add_texture(face)
    prg.set_uniform1i("u_overlaytex", t)
    
    vao.add_ebo(ebo)
    vao.add_primitive(GL_TRIANGLES, 0, 6)
    vao.unbind()

    return (vao,)

def render (vao):
    gl.clear()
    vao.render()
    flip()

def update (vao):
    now     = pygame.time.get_ticks()/1000
    #off     = math.sin(now) * 0.5
    #vao.set_uniform1i("u_texture", int(now)%2)

init()
args = setup()
run(args)

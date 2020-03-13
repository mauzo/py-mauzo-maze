import  pygame
from    pygame.locals   import *
import  math
import  numpy           as np
import  signal

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

def run (x):
    clock = pygame.time.Clock()
    while True:
        es = pygame.event.get()
        for e in es:
            if e.type == QUIT:
                return

        update(x)
        render(x)
        clock.tick(80)

vertices = np.array([
    [[-0.5, -0.5, 0],   [1, 0, 0]],
    [[0.5, -0.5, 0],    [0, 1, 0]],
    [[0, 0.5, 0],       [0, 0, 1]],
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

    prg     = make_shader()
    vbo     = gl.Buffer("vbo", vertices)
    #ebo     = gl.Buffer("ebo", indices)
    vao     = gl.VAO(prg)

    vao.add_vbo(vbo)
    vao.setup_attrib("b_pos",   3, 6, 0)
    #vao.setup_attrib("b_color", 3, 6, 3)
    #vao.add_ebo(ebo)
    vao.add_primitive(GL_TRIANGLES, 0, 3)
    vao.unbind()

    return vao

def render (vao):
    glClear(GL_COLOR_BUFFER_BIT)
    vao.render()
    flip()

def update (vao):
    now     = pygame.time.get_ticks()/1000
    off     = math.sin(now) * 0.5
    vao.set_uniform1f("u_offset", off)

init()
vao = setup()
run(vao)

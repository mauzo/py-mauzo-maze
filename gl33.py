import  pygame
from    pygame.locals   import *
import  numpy           as np
import  signal


# Do this last, since pygame.locals conflicts
from    OpenGL.GL       import *

import  mauzo.maze.gl   as gl

WINSIZE = (500, 500)

def eloop ():
    while True:
        e = pygame.event.wait()
        if e.type != MOUSEMOTION:
            print(e)
        if e.type == QUIT:
            return

def flip ():
    pygame.display.flip()

def sigint (x, y):
    raise KeyboardInterrupt()

def init ():
    signal.signal(signal.SIGINT, sigint)
    pygame.init()
    pygame.display.set_mode(WINSIZE, OPENGL|DOUBLEBUF)
    eloop()

triangle = np.array([
    [-0.5, -0.5, 0],
    [0.5, -0.5, 0],
    [0, 0.5, 0],
], dtype=GLfloat)

rectangle = np.array([
    [0.5, 0.5, 0],
    [0.5, -0.5, 0],
    [-0.5, -0.5, 0],
    [-0.5, 0.5, 0],
], dtype=GLfloat)

indices = np.array([
    0, 1, 3,
    1, 2, 3,
], dtype=GLint)

vertex_shader_src = b"""
#version 330 core

in vec3 pos;

void main ()
{
    gl_Position = vec4(pos.x, pos.y, pos.z, 1.0);
}
"""

frag_shader_src = b"""
#version 330 core

out vec4 color;

void main ()
{
    color = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""

def make_triangle_shader ():
    prg = gl.Shader()
    prg.add_shader("vertex", vertex_shader_src)
    prg.add_shader("fragment", frag_shader_src)
    prg.link()

    return prg

def setup ():
    glClearColor(0.2, 0.3, 0.3, 1.0)

    prg     = make_triangle_shader()
    vbo     = gl.Buffer("vbo", rectangle)
    ebo     = gl.Buffer("ebo", indices)
    vao     = gl.VAO(prg)

    vao.add_vbo(vbo)
    vao.setup_attrib("pos", 3, 3, 0)
    vao.add_ebo(ebo)
    vao.add_primitive(GL_TRIANGLES, 0, 6)
    vao.unbind()

    return vao

def render (vao):
    glClear(GL_COLOR_BUFFER_BIT)
    vao.render()
    flip()

init()
vao = setup()
print("Drawing...")
render(vao)

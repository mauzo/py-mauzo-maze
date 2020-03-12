import  pygame
from    pygame.locals   import *
import  numpy           as np
import  signal

# This is needed for the last parameter of glVertexAttribPointer. It is
# a void* when it should be an offset (historically it was a pointer but
# VBOs reinterpret it as an offset into the VBO) so the python bindings
# seem to get confused unless we cast with this.
from    ctypes          import c_void_p

# Do this last, since pygame.locals conflicts
from    OpenGL.GL       import *

WINSIZE = (500, 500)

def eloop ():
    return pygame.event.get()

def flip ():
    pygame.display.flip()

def sigint (x, y):
    raise KeyboardInterrupt()

def init ():
    signal.signal(signal.SIGINT, sigint)
    pygame.init()
    pygame.display.set_mode(WINSIZE, OPENGL|DOUBLEBUF)
    eloop()

vertices = np.array([
    [0.5, -0.5, 0],
    [0.5, -0.5, 0],
    [0, 0.5, 0],
], dtype=np.float32)

vertex_shader_src = b"""
#version 330 core
layout (location = 0) in vec3 aPos;

void main ()
{
    gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
}
"""

frag_shader_src = b"""
#version 330 core
out vec4 FragColor;

void main ()
{
    FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""

def compile_shader (typ, src):
    sh = glCreateShader(typ)
    glShaderSource(sh, [src])
    glCompileShader(sh)

    if not glGetShaderiv(sh, GL_COMPILE_STATUS):
        log = glGetShaderInfoLog(sh)
        raise RuntimeError("Shader compilation failed: " + log.decode())

    return sh

def link_shaders (shs):
    prg = glCreateProgram()
    for sh in shs:
        glAttachShader(prg, sh)
    glLinkProgram(prg)

    if not glGetProgramiv(prg, GL_LINK_STATUS):
        log = glGetShaderInfoLog(sh)
        raise RuntimeError("Shader link failed: " + log.decode())

    for sh in shs:
        glDeleteShader(sh)

    return prg

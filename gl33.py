import  pygame
from    pygame.locals   import *
import  numpy           as np
import  signal

# This is needed for the last parameter of glVertexAttribPointer. It is
# a void* when it should be an offset (historically it was a pointer but
# VBOs reinterpret it as an offset into the VBO) so the python bindings
# seem to get confused unless we cast with this.
from    ctypes          import c_void_p, sizeof

# Do this last, since pygame.locals conflicts
from    OpenGL.GL       import *

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

_buftypes = {
    "vbo":  GL_ARRAY_BUFFER,
    "ebo":  GL_ELEMENT_ARRAY_BUFFER,
}

class GLBuffer:
    __slots__ = ["targ", "id", "usage"]

    def __init__ (self, typ, data=None):
        self.targ   = _buftypes[typ]
        self.id     = glGenBuffers(1)

        print("Created", typ, "buffer", self.id)

        if data is not None:
            self.load(data)

    def delete (self):
        print("Deleting buffer", self.id)
        glDeleteBuffers(1, [self.id])

    def bind (self):
        glBindBuffer(self.targ, self.id)

    def unbind (self):
        glBindBuffer(self.targ, 0)

    def load (self, data):
        self.bind()
        glBufferData(self.targ, data, GL_STATIC_DRAW)

class GLVAO:
    __slots__ = ["id", "shader", "vbo", "ebo", "primitives"]

    def __init__ (self, shader):
        self.id         = glGenVertexArrays(1)
        self.shader     = shader
        self.vbo        = None
        self.ebo        = None
        self.primitives = []

        print("Created VAO", self.id)

    def delete (self):
        print("Deleting VAO", self.id)
        glDeleteVertexArrays(1, [self.id])
        if self.vbo is not None:
            self.vbo.delete()
        if self.ebo is not None:
            self.ebo.delete()

    def bind (self):
        glBindVertexArray(self.id)

    def unbind (self):
        glBindVertexArray(0)
        if self.vbo is not None:
            self.vbo.unbind()
        if self.ebo is not None:
            self.ebo.unbind()

    def add_vbo (self, vbo):
        self.vbo    = vbo

    def setup_attrib (self, att, size, stride, offset):
        ix = glGetAttribLocation(self.shader, att)

        self.bind()
        self.vbo.bind()
        glVertexAttribPointer(ix, size, GL_FLOAT, GL_FALSE,
            stride*sizeof(GLfloat), c_void_p(offset))
        glEnableVertexAttribArray(ix)

    def add_ebo (self, ebo):
        self.ebo    = ebo
        self.bind()
        ebo.bind()

    def add_primitive (self, mode, off, n):
        self.primitives.append((mode, off, n))

    def render (self):
        glUseProgram(self.shader)
        self.bind()

        for p in self.primitives:
            (mode, off, n) = p
            if self.ebo is None:
                glDrawArrays(mode, off, n)
            else:
                glDrawElements(mode, n, GL_UNSIGNED_INT, c_void_p(off))

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
    vs  = compile_shader(GL_VERTEX_SHADER, vertex_shader_src)
    fs  = compile_shader(GL_FRAGMENT_SHADER, frag_shader_src)
    prg = link_shaders([vs, fs])

    return prg

def setup ():
    glClearColor(0.2, 0.3, 0.3, 1.0)

    prg     = make_triangle_shader()
    vbo     = GLBuffer("vbo", rectangle)
    ebo     = GLBuffer("ebo", indices)
    vao     = GLVAO(prg)

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

import  math
import  numpy           as np
import  signal

import  pygame
from    pygame.locals   import *

import  glm
from    glm             import vec3, vec4, mat4, radians
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

    # depth
    glEnable(GL_DEPTH_TEST)
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
            #if e.type == KEYDOWN:
            #    handle_key(e.key, True)
            #if e.type == KEYUP:
            #    handle_key(e.key, False)

        update(clock.get_time()/1000, *args)
        render(*args)
        clock.tick(80)

cameraPos   = vec3(0, 0, 3)
cameraFront = vec3(0, 0, -1)
cameraUp    = vec3(0, 1, 0)

CAMERA_SPEED = 0.05

vertices = np.array([
    # vertex                texture
    -0.5, -0.5, -0.5,       0.0, 0.0,
     0.5, -0.5, -0.5,       1.0, 0.0,
     0.5,  0.5, -0.5,       1.0, 1.0,
     0.5,  0.5, -0.5,       1.0, 1.0,
    -0.5,  0.5, -0.5,       0.0, 1.0,
    -0.5, -0.5, -0.5,       0.0, 0.0,

    -0.5, -0.5,  0.5,       0.0, 0.0,
     0.5, -0.5,  0.5,       1.0, 0.0,
     0.5,  0.5,  0.5,       1.0, 1.0,
     0.5,  0.5,  0.5,       1.0, 1.0,
    -0.5,  0.5,  0.5,       0.0, 1.0,
    -0.5, -0.5,  0.5,       0.0, 0.0,

    -0.5,  0.5,  0.5,       1.0, 0.0,
    -0.5,  0.5, -0.5,       1.0, 1.0,
    -0.5, -0.5, -0.5,       0.0, 1.0,
    -0.5, -0.5, -0.5,       0.0, 1.0,
    -0.5, -0.5,  0.5,       0.0, 0.0,
    -0.5,  0.5,  0.5,       1.0, 0.0,

     0.5,  0.5,  0.5,       1.0, 0.0,
     0.5,  0.5, -0.5,       1.0, 1.0,
     0.5, -0.5, -0.5,       0.0, 1.0,
     0.5, -0.5, -0.5,       0.0, 1.0,
     0.5, -0.5,  0.5,       0.0, 0.0,
     0.5,  0.5,  0.5,       1.0, 0.0,

    -0.5, -0.5, -0.5,       0.0, 1.0,
     0.5, -0.5, -0.5,       1.0, 1.0,
     0.5, -0.5,  0.5,       1.0, 0.0,
     0.5, -0.5,  0.5,       1.0, 0.0,
    -0.5, -0.5,  0.5,       0.0, 0.0,
    -0.5, -0.5, -0.5,       0.0, 1.0,

    -0.5,  0.5, -0.5,       0.0, 1.0,
     0.5,  0.5, -0.5,       1.0, 1.0,
     0.5,  0.5,  0.5,       1.0, 0.0,
     0.5,  0.5,  0.5,       1.0, 0.0,
    -0.5,  0.5,  0.5,       0.0, 0.0,
    -0.5,  0.5, -0.5,       0.0, 1.0,
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
    #ebo     = gl.Buffer("ebo", indices)
    vao     = gl.VAO(prg)

    vao.add_vbo(vbo)
    vao.setup_attrib("b_pos",   3, 5, 0)
    vao.setup_attrib("b_tex",   2, 5, 3)

    t = vao.add_texture(cont)
    prg.set_uniform1i("u_basetex", t)
    t = vao.add_texture(face)
    prg.set_uniform1i("u_overlaytex", t)
    
    #vao.add_ebo(ebo)
    vao.add_primitive(GL_TRIANGLES, 0, 36)
    vao.unbind()

    return (vao,)

def render (vao):
    now     = pygame.time.get_ticks()/1000

    prg     = vao.shader

    aspect  = WINSIZE[0]/WINSIZE[1]
    proj    = glm.perspective(radians(45), aspect, 0.1, 100)
    prg.set_uniform_matrix4("u_proj", proj)

    view    = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp)
    prg.set_uniform_matrix4("u_view", view)

    vao.use()

    gl.clear()
    for i in range(len(cube_positions)):
        model   = mat4(1)
        model   = glm.translate(model, cube_positions[i])
        angle   = 20 * i
        if i % 3 == 0:
            angle += now * 50
        model   = glm.rotate(model, radians(angle), vec3(1, 0.3, 0.5))
        prg.set_uniform_matrix4("u_model", model)
        vao.render()
    flip()

def update (dt, vao):
    global cameraPos, cameraFront, cameraUp

    cameraSpeed = 2.5 * dt
    keys        = pygame.key.get_pressed()

    if keys[K_w]:
        cameraPos += cameraSpeed * cameraFront
    if keys[K_s]:
        cameraPos -= cameraSpeed * cameraFront
    if keys[K_a]:
        right = glm.normalize(glm.cross(cameraFront, cameraUp))
        cameraPos -= right * cameraSpeed
    if keys[K_d]:
        right = glm.normalize(glm.cross(cameraFront, cameraUp))
        cameraPos += right * cameraSpeed

init()
args = setup()
run(args)

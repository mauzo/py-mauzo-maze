import  glfw
from    OpenGL.GL      import *

def err (msg):
    raise RuntimeError(msg)

def handle_glfw_error (code, msg):
    err("glfw error: " + msg.decode())

def read_file (fname):
    with open(fname, "rb") as f:
        src = f.read()

    return src

if not glfw.init():
    err("failed to init glfw")
glfw.set_error_callback(handle_glfw_error)

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
#glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
window  = glfw.create_window(800, 600, "Hello world", None, None)

if not window:
    err("failed to create window")
glfw.make_context_current(window)
glfw.swap_interval(1)

src     = read_file("f-box.glsl")
shader  = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(shader, src)
glCompileShader(shader)

if not glGetShaderiv(shader, GL_COMPILE_STATUS):
    log = glGetShaderInfoLog(shader)
    err("Shader compilation failed: " + log.decode())

print("shader compiled successfully")

glClearColor(0, 0, 0, 1)
glColor4f(1, 0, 0, 1)
while not glfw.window_should_close(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.5, -0.5)
    glVertex2f(0.5, -0.5)
    glVertex2f(0, 0.5)
    glEnd()

    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.destroy_window(window)
glfw.terminate()

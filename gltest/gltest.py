import  glfw
from    OpenGL.GL      import *

def err (msg):
    raise RuntimeError(msg)

def handle_glfw_error (code, msg):
    err("glfw error: " + msg)

def read_file (fname):
    with open(fname, "rb") as f:
        src = f.read()

    return src

if not glfw.init():
    err("failed to init glfw")
glfw.set_error_callback(handle_glfw_error)

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
window  = glfw.create_window(800, 600, "Hello world", None, None)

if not window:
    err("failed to create window")
glfw.make_context_current(window)

src     = read_file("../glsl/f-box.glsl")
shader  = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(shader, src)
glCompileShader(shader)

if not glGetShaderiv(shader, GL_COMPILE_STATUS):
    log = glGetShaderInfoLog(shader)
    err("Shader compilation failed: " + log.decode())

print("shader compiled successfully")

glfw.destroy_window(window)
glfw.terminate()

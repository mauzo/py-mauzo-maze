# maze.py
# Playing with OpenGL

from mauzo.maze.app import *

app = get_app()
try:
    app.init()
    app.run()
finally:
    app.quit()

# GLFW
# Shader Sets
# shader classes with default methods

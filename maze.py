# maze.py
# Playing with OpenGL

from mauzo.maze.app import *

app = get_app()
try:
    app.init()
    app.run()
finally:
    app.quit()

# GLFW: fix pause and text
# Shader Sets
# shader classes with default methods
# shader includes

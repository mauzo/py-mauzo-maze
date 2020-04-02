# maze.py
# Playing with OpenGL

import  sys
import  mauzo.maze.app

app = mauzo.maze.app.MazeApp(sys.argv[1:])
try:
    app.init()
    app.run()
finally:
    app.quit()

# Shader Sets
# shader classes with default methods
# shader includes

# fix bump at corners

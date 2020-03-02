# world.py - World definitions
# This defines the world (the level layout).

from    OpenGL.GL   import *

from    .drawing    import *

# This is a private variable (it isn't imported when you import *). It
# holds our display list number
_DL = None

World = {
    # All the colours we use.
    "colours": {
        "Blue":     (0, 0, 0.5),
        "Green":    (0, 0.5, 0),
        "Red":      (0.5, 0, 0),
        "Grey":     (1, 1, 0.5),
        "Pink":     (1, 0, 1),
        "White":    (1, 1, 1),
        "Yellow":   (1, 1, 0),
    },

    # The player's starting position
    "start":      (-4, -8, -0.49),

    # A list of all the floors. Floors are horizontal rectangles. Each
    # floor has a dict with these keys:
    #   coords      A tuple of (x1, y1, x2, y2, z) defining the rectangle
    #   colour      A tuple of (red, green, blue)
    #   win         True if this is a winning platform, False otherwise
    "floors": [
        { "pos":        (-10, -10, -1),
          "edges":      ((20, 0, 0), (0, 20, 0)),
          "colour":     "Red",
          "win":        False,
        },
        { "pos":        (-10, 10, -1),
          "edges":      ((10, 0, 0), (0, 5, 0)),
          "colour":     "Green",
          "win":        False,
        },
        { "pos":        (0, 10, -1),
          "edges":      ((10, 0, 0), (0, 5, 0)),
          "colour":     "Blue",
          "win":        False,
        },
        { "pos":        (0, 0, 2),
          "edges":      ((5, 0, 0), (0, 5, 0)),
          "colour":     "Yellow",
          "win":        False,
        },
        { "pos":        (0, 6, 4),
          "edges":      ((5, 0, 0), (0, 5, 0)),
          "colour":     "Pink",
          "win":        False,
        },
        { "pos":        (6, 6, 6),
          "edges":      ((6, 0, 0), (0, 5, 0)),
          "colour":     "White",
          "win":        True,
        },
        { "pos":        (-10, 10, 3),
          "edges":      ((15, 0, 0), (0, 5, 0)),
          "colour":     "Grey",
          "win":        False,
        },
    ],

    # A list of the walls. Walls are parallelograms.
    "walls": [
        {   "pos":      (-10, -10, -1),
            "edges":    ((0, 0, 5), (10, 0, 0)),
            "colour":   "Blue",
        },
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}

# Build a display list representing the world, so we don't have to
# calculate all the triangles every frame.
def init_world():
    global _DL

    _DL = glGenLists(1)
    glNewList(_DL, GL_COMPILE)
    #draw_cube_10()
    draw_world_lights()
    draw_floors()
    draw_walls()
    draw_origin_marker()
    glEndList()

# Render the world using the display list
def render_world ():
    glCallList(_DL)

# Position our lights
def draw_world_lights ():
    glLightfv(GL_LIGHT0, GL_AMBIENT,    [0.3, 0.3, 0.3, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,    [0.7, 0.7, 0.7, 1])
    glLightfv(GL_LIGHT0, GL_POSITION,   [0.3, -1.2, 0.4, 0])

# Draw the floors out of World["floors"]. This breaks each rectangle into
# two triangles but doesn't subdivide any further; this will probably need
# changing when we get lights and/or textures.
FLOOR_THICKNESS = 0.2
def draw_floors ():
    col = World["colours"]
    for f in World["floors"]:
        colname = f["colour"]
        glColor(col[colname])

        p           = f["pos"]
        (e1, e2)    = f["edges"]
        e3          = [0, 0, -FLOOR_THICKNESS]
        
        new_select_name(colname)
        draw_ppiped(p, e1, e2, e3)

def draw_walls ():
    colours = World["colours"]
    for w in World["walls"]:
        c = w["colour"]
        glColor3f(*colours[c])

        p   = w["pos"]
        es  = w["edges"]

        new_select_name("wall-" + c)
        draw_pgram(p, *es)

# Find the floor below a given position.
# v is the point in space we want to start from.
# Returns one of the dictionaries from World["floors"], or None.
# This assumes floors are horizontal axis-aligned rectangles.
def find_floor_below(v):
    found = None
    for f in World["floors"]:
        pos = f["pos"]
        edg = f["edges"]

        if v[0] < pos[0] or v[1] < pos[1]:
            continue
        if v[0] > pos[0] + edg[0][0] or v[1] > pos[1]+edg[1][1]:
            continue
        if v[2] < pos[2]:
            continue
        if found and pos[2] <= found["pos"][2]:
            continue
        found = f
    return found

# Check if the player has moved outside the world and died.
def doomed (p):
    return p[2] < World["doom_z"]

# Return our starting position
def world_start_pos ():
    return World["start"]

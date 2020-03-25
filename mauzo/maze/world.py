# world.py - World definitions
# This defines the world (the level layout).

import  glm
from    glm         import  mat4, vec3, vec4
from    OpenGL.GL   import  *

from    .drawing    import *
from    .           import gl

_World = {
    # All the colours we use.
    "colours": {
        "Blue":     (0, 0, 0.5),
        "Green":    (0, 0.5, 0),
        "Red":      (0.5, 0, 0),
        "Grey":     (0.5, 0.5, 0.5),
        "Pink":     (0.8, 0, 1),
        "White":    (1, 1, 1),
        "Yellow":   (0.8, 0.8, 0),
    },

    # The player's starting position
    "start":      (-2, -2, -0.49),

    # The lights.
    "lights":   [
        {   "type":         "directional",
            "direction":    (0.3, -1.2, 0.4),
            "ambient":      (0.3, 0.3, 0.3),
            "diffuse":      (0.7, 0.7, 0.7),
            "specular":     (0.7, 0.7, 0.7),
        },
    ],

    # A list of all the floors. Floors are horizontal rectangles. Each
    # floor has a dict with these keys:
    #   pos         The coordinates of one corner
    #   edges       The vectors along the two edges, X first, then Y.
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
        { "pos":        (-7, 0, 1),
          "edges":      ((3, 0, 0), (0, 5, 0)),
          "colour":     "Green",
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
        { "pos":        (-13, -13, -5),
          "edges":      ((10, 0, 0), (0, 15, 0)),
          "colour":     "Pink",
          "win":        False,
        },
        { "pos":        (1, -13, -3),
          "edges":      ((8, 0, 0), (0, 2, 0)),
          "colour":     "Blue",
          "win":        False,
        },
        { "pos":        (8, -14, -3),
          "edges":      ((1, 0, 0), (0, 1, 0)),
          "colour":     "Blue",
          "win":        False,
        }
    ],

    # A list of the walls. Walls are parallelograms. The edges must be
    # given in anticlockwise order, looking at the side of the wall you
    # can see.
    "walls": [
        {   "pos":      (-9, -10, -1),
            "edges":    ((0, 0, 2), (17, 0, 0)),
            "colour":   ("Blue", "Yellow"),
        },
        {   "pos":      (9, -10, -1),
            "edges":    ((0, 0, 5), (1, 0, 0)),
            "colour":   ("Blue", "Yellow"),
        },
        {   "pos":      (-10, -10, -1),
            "edges":    ((0, 20, 0), (0, 0, 5)),
            "colour":   ("Blue", None),
        },
        {   "pos":      (10, -10, -1),
            "edges":    ((0, 0, 5), (0, 20, 0)),
            "colour":   ("Blue", None),
        },
        {   "pos":      (-10, 10, -1),
            "edges":    ((0, 5, 0), (0, 0, 5)),
            "colour":   ("Red", None),
        },
        {   "pos":      (-10, 15, -1),
            "edges":    ((10, 0, 0), (0, 0, 5)),
            "colour":   ("Red", None),
        },
        {   "pos":      (10, 10, -1),
            "edges":    ((0, 0, 5), (0, 5, 0)),
            "colour":   ("Green", None),
        },
        {   "pos":      (0, 15, -1),
            "edges":    ((10, 0, 0), (0, 0, 5)),
            "colour":   ("Green", None),
        },
    ],

    "keys": [
        {   "pos":      (0, 0, 0),
        },
        {   "pos":      (0, 0, -4.8),
            "colour":   "Green",
        },
    ],

    "collide": [
        {   "pos":      (0, 0, 0),
            "edges":    ((2, 0, 0), (0, 2, 0), (0, 0, -2)),
        },
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}

class Key:
    __slots__ = [
        "world",    # the world we are in
        "model",    # our model
        "pos",      # the position
    ]

    def __init__ (self, world, pos):
        self.world  = world
        self.pos    = vec3(pos)

        app         = world.app
        render      = app.render
        self.model  = render.load_model("key")

    def render (self, prg):
        model   = glm.translate(mat4(1), self.pos)
        normal  = gl.make_normal_matrix(model)

        prg.use()
        prg.u_model(model)
        prg.u_normal_matrix(normal)
        self.model.render(prg)

FLOOR_THICKNESS = 0.2

class World:
    __slots__ = [
        "app",              # Our app
        "collision_list",   # Used to detect collisions
        "dl",               # A displaylist to render the world
        "doom_z",           # We die if we fall this low
        "keys",             # The keys in this level
        "start",            # The player's starting position
    ]

    def __init__ (self, app):
        self.app    = app

    def init (self):
        self.start  = [c for c in _World["start"]]
        self.doom_z = _World["doom_z"]
        self.init_dl(_World)
        self.init_shader_lights(_World)
        self.init_keys(_World)
        self.init_collision(_World)

    def init_collision (self, level):
        planes = []
        for f in level["collide"]:
            p           = vec3(f["pos"])
            e1, e2, e3  = (vec3(e) for e in f["edges"])
            px          = p + e1 + e2 + e3
            planes.append((
                plane_from_points(p, e1, e2),
                plane_from_points(p, e2, e3),
                plane_from_points(p, e3, e1),
                plane_from_points(px, e2, e1),
                plane_from_points(px, e3, e2),
                plane_from_points(px, e1, e3),
            ))

        self.collision_list = planes
        print("Collision:", planes)

    # Build a display list representing the world, so we don't have to
    # calculate all the triangles every frame.
    def init_dl (self, level):
        self.dl = glGenLists(1)
        glNewList(self.dl, GL_COMPILE)
        #draw_cube_10()
        self.draw_lights(level)
        self.draw_floors(level)
        self.draw_walls(level)
        self.draw_collision(level)
        draw_origin_marker()
        glEndList()

    def init_shader_lights (self, level):
        prg     = self.app.render.shader
        light   = level["lights"][0]
        
        prg.u_sun_direction(vec3(light["direction"]))
        prg.u_sun_color_ambient(vec3(light["ambient"]))
        prg.u_sun_color_diffuse(vec3(light["diffuse"]))
        prg.u_sun_color_specular(vec3(light["specular"]))

    def init_keys (self, level):
        col     = level["colours"]
        keys    = []
        for k in level["keys"]:
            keys.append(Key(self, k["pos"]))

        self.keys = keys

    # Render the world using the display list
    def render (self):
        glCallList(self.dl)
        for k in self.keys:
            draw_point((0, 1, 1), list(k.pos))

    # Render the keys. Since this uses shader rendering it needs to be
    # separate from .render above.
    def render_keys (self, prg):
        for k in self.keys:
            k.render(prg)

    # Position our lights
    def draw_lights (self, level):
        for i, l in enumerate(level["lights"]):
            ix  = GL_LIGHT0 + i
            glLightfv(ix, GL_AMBIENT,   [*l["ambient"], 1])
            glLightfv(ix, GL_DIFFUSE,   [*l["diffuse"], 1])
            glLightfv(ix, GL_SPECULAR,  [*l["specular"], 1])
            glLightfv(ix, GL_POSITION,  [*l["direction"], 0])

    # Draw the floors out of World["floors"]. This breaks each rectangle
    # into two triangles but doesn't subdivide any further; this will
    # probably need changing when we get lights and/or textures.
    def draw_floors (self, level):
        col = level["colours"]
        for f in level["floors"]:
            colname = f["colour"]
            glColor(col[colname])

            p           = f["pos"]
            (e1, e2)    = f["edges"]
            e3          = [0, 0, -FLOOR_THICKNESS]
            
            draw_ppiped(p, e1, e2, e3)

    def draw_collision (self, level):
        glColor(1, 1, 1, 1)
        for f in level["collide"]:
            draw_ppiped(f["pos"], *f["edges"])

    def draw_walls (self, level):
        colours = level["colours"]
        for w in level["walls"]:
            p   = w["pos"]
            es  = w["edges"]
            c   = w["colour"]

            if c[0] is not None:
                glColor3f(*colours[c[0]])
                draw_pgram(p, es[0], es[1])
            if c[1] is not None:
                glColor3f(*colours[c[1]])
                draw_pgram(p, es[1], es[0])

    # Find the floor below a given position.
    # v is the point in space we want to start from.
    # Returns one of the dictionaries from World["floors"], or None.
    # This assumes floors are horizontal axis-aligned rectangles.
    def find_floor_below(self, v):
        found = None
        # XXX this still references World as this will go soon
        for f in _World["floors"]:
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

    def collision (self, p, margin):
        for o in self.collision_list:
            # Assume we collide with this object.
            collide = True
            print("collision for", p)
            for pl in o:
                # If we are outside any of the planes...
                print("  p .", repr(pl), "=", glm.dot(vec4(p, 1), pl))
                if glm.dot(vec4(p, 1), pl) > margin:
                    # we do not collide.
                    collide = False
            if collide:
                return True
        return False

    # Check if the player has moved outside the world and died.
    def doomed (self, p):
        return p[2] < self.doom_z

    # Return our starting position
    def start_pos (self):
        return self.start

# Given a plane x = p + sa + tb return the vec4(A,B,C,D) where
# vec3(A,B,C) is normal to the plane and Ax + By + Cz + D = 0 is an
# equation of the plane. 
def plane_from_points (p, a, b):
    n   = glm.normalize(glm.cross(a, b))
    d   = -glm.dot(n, p)
    return vec4(n, d)

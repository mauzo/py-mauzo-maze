# world.py - World definitions
# This defines the world (the level layout).

import  numpy       as      np
from    OpenGL.GL   import  *

from    .drawing    import *
from    .exceptions import *
from    .geometry   import *
from    .           import gl
from    .items      import *

FLOOR_THICKNESS = 0.2

class World:
    __slots__ = [
        "app",              # Our app
        "collision_list",   # Used to detect collisions
        "dl",               # A displaylist to render the world
        "doom_z",           # We die if we fall this low
        "items",            # The items on this level
        "level",            # The current level name
        "start",            # The player's starting position
        "start_angle",      # The player's starting angle
    ]

    def __init__ (self, app):
        self.app    = app

        if len(app.argv):
            self.level  = app.argv[0]
        else:
            self.level  = "start"

    def init (self):
        self._load_level()

    def reset (self):
        for i in self.items:
            i.reset()

    def read_level (self, level):
        fp  = open("levels/%s.py" % level, "r")
        py  = fp.read()
        fp.close()

        # XXX I don't like this. Something safer than running eval on
        # Python code would be nice, but most of the obvious
        # alternatives are annoying.
        return eval(py)
    
    def load_level (self, name):
        self.level  = name
        self._load_level()

    def _load_level (self):
        level       = self.read_level(self.level)

        self.start          = vec3(level["start"])
        self.start_angle    = level["start_angle"]
        self.doom_z         = level["doom_z"]

        self.init_dl(level)
        self.init_shader_lights(level)
        self.init_items(level)
        self.init_collision(level)

    def init_collision (self, level):
        coll = []
        for f in level["floors"]:
            p           = vec3(f["pos"])
            e1, e2      = (vec3(e) for e in f["edges"])
            e3          = vec3(0, 0, -FLOOR_THICKNESS)
            px          = p + e1 + e2 + e3
            coll.append((
                plane_from_vectors(p, e1, e2),
                plane_from_vectors(p, e2, e3),
                plane_from_vectors(p, e3, e1),
                plane_from_vectors(px, e2, e1),
                plane_from_vectors(px, e3, e2),
                plane_from_vectors(px, e1, e3),
            ))

        for w in level["walls"]:
            p           = vec3(w["pos"])
            e1, e2, e3  = (vec3(e) for e in w["edges"]) 
            px          = p + e1 + e2 + e3
            coll.append((
                plane_from_vectors(p, e1, e2),
                plane_from_vectors(p, e2, e3),
                plane_from_vectors(p, e3, e1),
                plane_from_vectors(px, e2, e1),
                plane_from_vectors(px, e3, e2),
                plane_from_vectors(px, e1, e3),
            ))

        self.collision_list = coll
        print("Collision:", coll)

    # Build a display list representing the world, so we don't have to
    # calculate all the triangles every frame.
    def init_dl (self, level):
        self.dl = glGenLists(1)
        glNewList(self.dl, GL_COMPILE)
        #draw_cube_10()
        self.draw_lights(level)
        self.draw_floors(level)
        self.draw_walls(level)
        draw_origin_marker()
        glEndList()

    def init_shader_lights (self, level):
        prg     = self.app.render.shader
        light   = level["lights"][0]
        
        prg.use()
        prg.u_sun_direction(vec3(light["direction"]))
        prg.u_sun_color_ambient(vec3(light["ambient"]))
        prg.u_sun_color_diffuse(vec3(light["diffuse"]))
        prg.u_sun_color_specular(vec3(light["specular"]))

    def init_items (self, level):
        items   = []
        # XXX We look up the class for each item in the current module.
        # This is perhaps not the best idea...
        classes = globals()

        for i in level["items"]:
            Cls = classes[i["type"]]
            items.append(Cls(world=self, **i))

        self.items  = items

    # Render the world using the display list
    def render (self):
        glCallList(self.dl)

    # Render the keys. Since this uses shader rendering it needs to be
    # separate from .render above.
    def render_items (self, ctx):
        for i in self.items:
            i.render(ctx)

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

    def draw_walls (self, level):
        colours = level["colours"]
        for w in level["walls"]:
            p   = w["pos"]
            es  = w["edges"]
            c   = w["colour"]

            glColor3f(*colours[c])
            draw_ppiped(p, *es)

    # We have just moved from 'old' to 'new'.
    # margin is the bump margin.
    def collision (self, old, new, margin):
        old4    = vec4(old, 1)
        new4    = vec4(new, 1)
        for pls in self.collision_list:
            # Assume we collide with this object.
            collide = True
            outside  = []
            for pl in pls:
                d   = glm.dot(new4, pl)
                # If we are outside any of the planes...
                if d > margin:
                    # we do not collide.
                    collide = False
                    break
                elif d > 0:
                    outside.append(pl)
            if collide:
                if len(outside) > 1:
                    print("Collision, outside", outside)
                # Find the plane we collided with
                for pl in pls:
                    if glm.dot(old4, pl) > margin:
                        break
                return vec3(pl)
        return None

    def check_item_collisions (self, player):
        for item in self.items:
            if item.collide(player.pos, player.bump):
                item.activate(player)
    
    # Check if the player has moved outside the world and died.
    def doomed (self, p):
        return p.z < self.doom_z


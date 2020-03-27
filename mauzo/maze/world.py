# world.py - World definitions
# This defines the world (the level layout).

from    OpenGL.GL   import  *

from    .drawing    import *
from    .geometry   import *
from    .           import gl

PI = glm.pi()

class Key:
    __slots__ = [
        "world",    # the world we are in
        "model",    # our model
        "pos",      # the position
        "visible",  # Can you  see it?
    ]

    def __init__ (self, world, pos):
        self.world  = world
        self.pos    = vec3(pos)

        app          = world.app
        render       = app.render
        self.model   = render.load_model("key")
        self.visible = True  

    def render (self, ctx):
        prg     = ctx.shader
        now     = ctx.now
        model   = glm.translate(mat4(1), self.pos)
        model   = glm.scale(model, vec3(0.2))
        model   = glm.rotate(model, 0.8 * PI * now, vec3(0, 0, 1))
        model   = glm.rotate(model, PI/3, vec3(0, 1, 0))
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
        "floors",           # XXX the floors out of the level file
        "keys",             # The keys in this level
        "level",            # The current level name
        "_next_level",      # The name of the next level, or None
        "start",            # The player's starting position
        "start_angle",
    ]

    def __init__ (self, app):
        self.app    = app

    def init (self):
        self.level  = "start"
        self.load_level()

    def next_level (self):
        if not self._next_level:
            return False

        self.level  = self._next_level
        self.load_level()
        return True

    def read_level (self, level):
        fp  = open("levels/%s.py" % level, "r")
        py  = fp.read()
        fp.close()

        # XXX I don't like this. Something safer than running eval on
        # Python code would be nice, but most of the obvious
        # alternatives are annoying.
        return eval(py)
    
    def load_level (self):
        level       = self.read_level(self.level)

        self.start          = vec3(level["start"])
        self.start_angle    = level["start_angle"]
        self.doom_z         = level["doom_z"]
        self.floors         = level["floors"]

        if "next_level" in level:
            self._next_level = level["next_level"]
        else:
            self._next_level = None

        self.init_dl(level)
        self.init_shader_lights(level)
        self.init_keys(level)
        self.init_collision(level)

    def init_collision (self, level):
        coll = []
        for f in level["floors"]:
            p           = vec3(f["pos"])
            e1, e2      = (vec3(e) for e in f["edges"])
            e3          = vec3(0, 0, -FLOOR_THICKNESS)
            px          = p + e1 + e2 + e3
            coll.append((
                f["win"],
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
                f["win"],
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

    # Render the keys. Since this uses shader rendering it needs to be
    # separate from .render above.
    def render_keys (self, ctx):
        for k in self.keys:
            if k.visible:
                k.render(ctx)

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

            glColor3f(*colours[c])
            draw_ppiped(p, *es)

    # Find the floor below a given position.
    # v is the point in space we want to start from.
    # Returns one of the dictionaries from World["floors"], or None.
    # This assumes floors are horizontal axis-aligned rectangles.
    def find_floor_below(self, v):
        found = None
        for f in self.floors:
            pos = f["pos"]
            edg = f["edges"]

            if v.x < pos[0] or v.y < pos[1]:
                continue
            if v.x > pos[0] + edg[0][0] or v.y > pos[1]+edg[1][1]:
                continue
            if v.z < pos[2]:
                continue
            if found and pos[2] <= found["pos"][2]:
                continue
            found = f
        return found

    # We have just moved from 'old' to 'new'.
    # margin is the bump margin.
    def collision (self, old, new, margin):
        old4    = vec4(old, 1)
        new4    = vec4(new, 1)
        for obj, *pls in self.collision_list:
            # Assume we collide with this object.
            collide = True
            for pl in pls:
                # If we are outside any of the planes...
                if glm.dot(new4, pl) > margin:
                    # we do not collide.
                    collide = False
                    break
            if collide:
                # Find the plane we collided with
                for pl in pls:
                    if glm.dot(old4, pl) > margin:
                        break
                return obj, vec3(pl)
        return None

    def key_collision (self, player):
        for key in self.keys:
            if glm.length(player - key.pos) < 1:
                return key
        return None
                     
    # Check if the player has moved outside the world and died.
    def doomed (self, p):
        return p.z < self.doom_z

    # Return our starting position
    def start_pos (self):
        return self.start


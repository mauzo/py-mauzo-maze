# player.py - The player character

import  math
from    OpenGL.GL       import *
from    OpenGL.GLU      import *

from    .exceptions     import *
from    .geometry       import *

class Player:
    __slots__ = [
        "app",          # A ref to our app
        "damage",       # Are we being damaged right now?
        "damage_time",  # When you last took damage
        "DL",           # Our display list number
        "facing",       # Our current facing direction (a quaternion)
        "falling",      # Are we falling?
        "have_key",     # Do we have the key?
        "hearts",       # How many hearts we have
        "jumping",      # True if we are currently jumping.
        "pos",          # Our current position
        "vel",          # Our current velocity
        "world",        # The world
        "walking",      # Our current walk speed.
    ]

    def __init__ (self, app):
        self.app    = app
        self.world  = app.world

        # This will be updated by the camera
        self.facing     = quat()
        self.walking    = zero3

        self.hearts         = 3
        self.damage         = False
        self.damage_time    = 0

    def init (self):
        # Compile a display list.
        self.DL = glGenLists(1)
        glNewList(self.DL, GL_COMPILE)
        self.draw()
        glEndList()

        self.reset()

    def respawn (self):
        self.pos        = self.world.start
        self.vel        = zero3
        self.jumping    = False
        self.falling    = False
        print("RESPAWN")
        
    def reset (self):
        self.respawn()
        self.have_key   = False
        self.hearts     = 3
        print("RESET", self.pos, self.vel)

    # The speeds at which the player walks, jumps and falls.
    # These numbers don't make sense to me; possibly I'm expecting the
    # player to jump unrealistically high. If I don't make the jump speed
    # high enough the player hardly gets off the ground, but then gravity
    # has to be really high or we hang in the air for ages.
    speed = {
        "walk":     8.0,        # m/s
        "jump":     8.0,        # m/s
        "fall":    16.0,        # m/s^2
    }

    # Draw the player as a wireframe sphere.
    def draw (self):
        glPushAttrib(GL_CURRENT_BIT|GL_ENABLE_BIT)
        # We scale anamorphically, so we need to renormalise normals
        glEnable(GL_NORMALIZE)

        q = gluNewQuadric()
        gluQuadricDrawStyle(q, GLU_LINE)
        glColor3f(1.0, 1.0, 1.0)
        gluSphere(q, 0.5, 16, 16);
        gluDeleteQuadric(q)

        glPopAttrib()

    # Render the player
    def render (self):
        p   = self.pos
        v   = self.vel

        s = vec3(0.015, 0.015, 0.0075) * glm.abs(v) + vec3(1)

        glPushMatrix()
        glTranslate(*p)
        glScalef(*s)
        glCallLists(self.DL)
        glPopMatrix()

    # Set our facing direction
    def face (self, angle):
        self.facing = glm.rotate(quat(), radians(angle), Zpos)

    # Set how we're trying to walk. We will only move if we're on the
    # ground. Don't attempt to set a Z coordinate
    def walk (self, v):
        self.walking += self.speed["walk"] * v

    # Set the flag to show we're jumping. We will only jump if we're on the
    # ground.
    def jump (self, j):
        self.jumping = j

    def set_damage (self):
        self.damage = True

    def lose_heart (self):
        h = self.hearts - 1
        self.hearts = h
        if h == 0:
            raise XDie()

    bump = 0.49

    # See if we can fall. Returns None if we can fall, or the normal of
    # the floor if we can't.
    def find_floor (self, dt):
        pos     = self.pos
        vel     = self.vel
        world   = self.world

        dv_z    = -self.speed["fall"] * dt    
        if self.falling:
            vel = vec3(vel.xy, vel.z + dv_z)
        else:
            vel = vec3(0, 0, dv_z)

        npos    = pos + vel * dt
        hit     = world.collision(pos, npos, self.bump)

        if hit:
            if self.falling:
                self.fall_damage()
                self.vel    = vec3(0)
            self.falling    = False
            return hit

        self.pos        = npos
        self.vel        = vel
        self.falling    = True
        return None

    def walk_velocity (self, floor, dt):
        # Rotate our 'walking' speed by our 'facing' direction
        walk    = self.facing * self.walking
        walk_n  = glm.normalize(walk)

        print(f"walk_velocity: floor {floor!r} walk {walk!r}")
        
        if self.jumping:
            vel             = vec3(walk.xy, self.speed["jump"])
            self.jumping    = False
            self.falling    = True
        elif glm.length(floor) == 0:
            vel     = walk
        elif glm.dot(walk_n, floor) > -0.5:
            vel     = project_onto_plane(floor, walk)
            #vel     *= glm.clamp(1 + 2 * cos_th, 0, 1)
        else:
            if walk != zero3:
                print(f"Cannot walk, too steep: {floor!r}")
            vel = vec3(0)

        return vel 

    def check_collisions (self, vel, dt):
        pos     = self.pos
        world   = self.world

        print(f"check_collisions: vel {vel!r}")
        npos    = pos + vel * dt
        hit     = world.collision(pos, npos, self.bump)
        if hit:
            vel     = project_onto_plane(hit, vel)
            npos    = pos + vel * dt
            hit     = world.collision(pos, npos, self.bump)
            if hit:
                vel     = zero3
                npos    = pos

        self.pos    = npos
        self.vel    = vel

    def update_position (self, dt):
        floor   = self.find_floor(dt)
        if not floor:
            return

        vel     = self.walk_velocity(floor, dt)
        self.check_collisions(vel, dt)

    # Run the player physics. dt the time since the last frame, in seconds.
    def update (self, ctx):
        # Assume we don't need to take damage
        self.damage = False

        self.update_position(ctx.dt)
        pos     = self.pos
        world   = self.world

        world.check_item_collisions(self)

        self.check_damage(ctx)
        self.check_doomed()

    # If we have collided with something that damages us, lose hearts
    def check_damage(self, ctx):
        if self.damage:
            print("damage", ctx.now, self.damage_time)
            if ctx.now - self.damage_time > 1:
                self.lose_heart()
                self.damage_time = ctx.now
                
    def fall_damage(self):
        print("fall speed", self.vel.z),
        if self.vel.z < -16:
            self.damage = True

    # If we fall too far we die.
    def check_doomed(self):
        if self.world.doomed(self.pos):
            self.lose_heart()
            raise XRespawn()
          

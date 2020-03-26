# player.py - The player character

import  glm
from    glm             import quat, radians, vec2, vec3, vec4
from    OpenGL.GL       import *
from    OpenGL.GLU      import *

EPSILON = 0.0001

class Player:
    __slots__ = [
        "app",          # A ref to our app
        "DL",           # Our display list number
        "pos",          # Our current position
        "vel",          # Our current velocity
        "walking",      # Our current walk speed.
        "facing",       # Our current facing direction (a quaternion)
        "jumping",      # True if we are currently jumping.
        "stopped",      # The time we were last stopped.
        "have_key",     # Do we have the key?
    ]

    def __init__ (self, app):
        self.app    = app

        self.walking    = vec3(0)
        # This will be updated by the camera
        self.facing     = quat()
        self.jumping    = False
        self.stopped    = 0
        self.have_key   = False

    def init (self):
        # Compile a display list.
        self.DL = glGenLists(1)
        glNewList(self.DL, GL_COMPILE)
        self.draw()
        glEndList()

        self.reset()

    def reset (self):
        self.pos    = self.app.world.start_pos()
        self.vel    = vec3(0)
        print("RESET", self.pos, self.vel)

    # The speeds at which the player walks, jumps and falls.
    # These numbers don't make sense to me; possibly I'm expecting the
    # player to jump unrealistically high. If I don't make the jump speed
    # high enough the player hardly gets off the ground, but then gravity
    # has to be really high or we hang in the air for ages.
    speed = {
        "walk":     8.0,        # m/s
        "jump":     8.0,        # m/s
        "fall":     16.0,       # m/s^2
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

        s = vec3(0.015, 0.015, 0.0075) * v + vec3(1)

        glPushMatrix()
        glTranslate(*p)
        glScalef(*s)
        glCallLists(self.DL)
        glPopMatrix()

    # Set our facing direction
    def face (self, angle):
        self.facing = glm.rotate(quat(), radians(angle), vec3(0, 0, 1))

    # Set how we're trying to walk. We will only move if we're on the
    # ground. Don't attempt to set a Z coordinate
    def walk (self, v):
        self.walking += self.speed["walk"] * v

    # Set the flag to show we're jumping. We will only jump if we're on the
    # ground.
    def jump (self):
        self.jumping = True

    bump = 0.49

    # Run the player physics. dt the time since the last frame, in seconds.
    def physics(self, dt):
        pos     = self.pos
        vel     = self.vel
        now     = self.app.now()
        world   = self.app.world

        # Assume we are falling.
        falling     = True

        # Find the floor below us. If there is a floor, and we are close
        # enough to it, we are not falling.
        floor = world.find_floor_below(pos)
        if (floor):
            floor_z = floor["pos"][2] + self.bump 
            if (pos.z <= floor_z and vel.z <= 0):
                falling = False
                if (floor["win"]):
                    self.app.win()
                    return

        if falling:
            # If we are falling, increase our velocity in the downwards
            # z direction by the fall speed (actually an acceleration).
            v_z     = vel.z - self.speed["fall"] * dt
            # If we have only just moved, remove our sideways velocity
            # so we fall straight down.
            if now - self.stopped < 0.2:
                vel = vec3(0, 0, v_z)
            else:
                vel = vec3(vel.xy, v_z)
        else:
            # Otherwise, set our velocity to our walk vector rotated to the
            # direction we are facing. This is a quaternion multiply,
            # which rotates the vector using the quaternion.
            walk    = self.facing * self.walking
            # Then, if we are jumping, set our z velocity to be the jump speed
            # and turn off the jump (we only jump once).
            if self.jumping:
                v_z = self.speed["jump"]
                self.jumping = False
            else:
                v_z = 0
            vel = vec3(walk.xy, v_z)

        # Take the velocity vector we have calculated and add it to our
        # position vector to give our new position. Multiply the
        # velocity by the time taken to render the last frame so our
        # speed is independant of the FPS.
        pos = pos + vel * dt

        # If we would collide, we don't move.
        if world.collision(pos, self.bump):
            vel = vec3(0)

        key = world.key_collision(pos)
        if key:
            self.have_key = True
            key.visible = False

        # Save our velocity for next time
        self.vel = vel

        # If we aren't moving, record that we stopped and return.
        if vel == vec3(0):
            self.stopped = now
            return

        # If we have fallen through the floor put us back on top of the floor
        # so that we land on it.
        if floor and pos.z <= floor_z and vel.z <= 0:
            pos = vec3(pos.xy, floor_z - EPSILON)

        # If we fall too far we die.
        if world.doomed(pos):
            self.app.die()
            return

        # Save our new position.
        self.pos = pos

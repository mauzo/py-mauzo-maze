# player.py - The player character

from    OpenGL.GL       import *
from    OpenGL.GLU      import *

from    .vectors    import *
from    .world      import doomed, find_floor_below, world_start_pos

class Player:
    __slots__ = [
        # A ref to our app
        "app",
        # Our display list number
        "DL",
        # Our current position
        "pos",
        # Our current veolcity (our speed in the X, Y and Z directions)
        "vel",
        # Our current walk speed.
        "walking",
        # Our current facing direction (a quaternion)
        "facing",
        # True if we are currently jumping.
        "jumping",
        # The time we were last stopped.
        "stopped",
    ]

    def __init__ (self, app):
        self.app    = app

        # Find our starting position from the world definition. We need
        # to change this from a tuple to a list since we need it to be
        # modifiable.
        self.pos    = [c for c in world_start_pos()]

        self.vel        = [0, 0, 0]
        self.walking    = [0, 0, 0]
        # This will be updated by the camera
        self.facing     = [0, 0, 0, 0]
        self.jumping    = False
        self.stopped    = 0

    def init (self):
        # Compile a display list.
        self.DL = glGenLists(1)
        glNewList(self.DL, GL_COMPILE)
        self.draw()
        glEndList()

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

        s   = [abs(v[0])*0.015 + 1, abs(v[1])*0.015 + 1, abs(v[2])*0.0075 + 1]

        glPushMatrix()
        glTranslate(*p)
        glScalef(*s)
        glCallLists(self.DL)
        glPopMatrix()

    # Set our facing direction
    def face (self, angle):
        self.facing = quat_rotate_about(angle, [0, 0, 1])

    # Set how we're trying to walk. We will only move if we're on the
    # ground. Don't attempt to set a Z coordinate
    def walk (self, v):
        self.walking = vec_add(self.walking, 
            vec_mul(v, self.speed["walk"]))

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

        # Assume we are falling.
        falling     = True

        # Find the floor below us. If there is a floor, and we are close
        # enough to it, we are not falling.
        floor = find_floor_below(pos)
        if (floor):
            floor_z = floor["pos"][2] + self.bump 
            if (pos[2] <= floor_z and vel[2] <= 0):
                falling = False
                if (floor["win"]):
                    self.app.win()
            #else:
                #("Falling through floor", floor)

        if (falling):
            # If we are falling, increase our velocity in the downwards
            # z direction by the fall speed (actually an acceleration). 
            vel[2] -= dt * self.speed["fall"]
            # If we have only just moved, remove our sideways velocity
            # so we fall straight down.
            if now - self.stopped < 200:
                vel[0] = 0
                vel[1] = 0
        else:
            # Otherwise, set our velocity to our walk vector rotated to the
            # direction we are facing.
            vel     = quat_apply(self.facing, self.walking)
            # Then, if we are jumping, set our z velocity to be the jump speed
            # and turn off the jump (we only jump once).
            if (self.jumping):
                vel[2] = self.speed["jump"]
                self.jumping = False

        # Save our velocity for next time
        self.vel = vel

        # If we aren't moving, record that we stopped and return.
        if (vel == [0, 0, 0]):
            self.stopped = now
            return

        # Take the velocity vector we have calculated and add it to our position
        # vector to give our new position. Multiply the velocity by the time
        # taken to render the last frame so our speed is independant of the
        # FPS.
        pos = vec_add(pos, vec_mul(vel, dt))

        # If we have fallen through the floor put us back on top of the floor
        # so that we land on it.
        if (floor and pos[2] < floor_z and vel[2] <= 0):
            pos[2] = floor_z

        #print("Player move from", Player["pos"])
        #print("    to", pos)
        #print("    falling", falling, "floor", 
            #(floor["colour"] if floor else "<none>"))

        # If we fall too far we die.
        if (doomed(pos)):
            self.app.die()

        # Save our new position.
        self.pos = pos


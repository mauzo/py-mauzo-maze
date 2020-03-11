# player.py - The player character

from    OpenGL.GL       import *
from    OpenGL.GLU      import *

# This dict has information about the player.
# This must appear before the imports below because camera.py uses it.
Player = {
    # Our current position
    "pos":      [0, 0, 0],
    # Our current veolcity (our speed in the X, Y and Z directions)
    "vel":      [0, 0, 0],
    # Our current walk speed.
    "walk":     [0, 0, 0],
    # True if we are currently jumping.
    "jump":     False,
}

from    .           import app
from    .camera     import Camera
from    .vectors    import *
from    .world      import doomed, find_floor_below, world_start_pos

# The speeds at which the player walks, jumps and falls.
# These numbers don't make sense to me; possibly I'm expecting the
# player to jump unrealistically high. If I don't make the jump speed
# high enough the player hardly gets off the ground, but then gravity
# has to be really high or we hang in the air for ages.
Speed = {
    "walk":     8.0,        # m/s
    "jump":     8.0,        # m/s
    "fall":     16.0,       # m/s^2
}

# This is a private variable to hold our display list number.
_DL = None

def init_player ():
    global _DL

    # Find our starting position from the world definition. We need to
    # change this from a tuple to a list since we need it to be
    # modifiable.
    Player["pos"] = [c for c in world_start_pos()]

    # Compile a display list.
    _DL = glGenLists(1)
    glNewList(_DL, GL_COMPILE)
    draw_player()
    glEndList()

# Draw the player as a wireframe sphere.
def draw_player ():
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
def render_player ():
    p   = Player["pos"]
    v   = Player["vel"]

    s   = [abs(v[0])*0.015 + 1, abs(v[1])*0.015 + 1, abs(v[2])*0.0075 + 1]

    glPushMatrix()
    glTranslate(*p)
    glScalef(*s)
    glCallLists(_DL)
    glPopMatrix()

# The player has died...
def player_die ():
    print("AAAARGH!!!")
    app.event_post_quit()

# The player has won...
def player_win ():
    print("YaaaY!!!!")
    app.event_post_quit()

# Set how we're trying to walk. We will only move if we're on the
# ground. Don't attempt to set a Z coordinate
def player_walk (v):
    Player["walk"] = vec_add(Player["walk"], vec_mul(v, Speed["walk"]))

# Set the flag to show we're jumping. We will only jump if we're on the
# ground.
def player_jump (to):
    Player["jump"] = to

# Return our current position
def pos ():
    return Player["pos"]

PLAYER_BUMP = 0.49

# Run the player physics. dt the time since the last frame, in seconds.
def player_physics(dt):
    pos     = Player["pos"]
    vel     = Player["vel"]
    walk    = Player["walk"]
    jump    = Player["jump"]

    walk_q  = Camera["walk_quat"]

    # Assume we are falling.
    falling     = True

    # Find the floor below us. If there is a floor, and we are close
    # enough to it, we are not falling.
    floor = find_floor_below(pos)
    if (floor):
        floor_z = floor["pos"][2] + PLAYER_BUMP
        if (pos[2] <= floor_z and vel[2] <= 0):
            falling = False
            if (floor["win"]):
                player_win()
        #else:
            #("Falling through floor", floor)

    if (falling):
        # If we are falling, increase our velocity in the downwards z direction
        # by the fall speed (actually an acceleration). 
        vel[2] -= dt * Speed["fall"]
    else:
        # Otherwise, set our velocity to our walk vector rotated to the
        # camera angle.
        vel = quat_apply(walk_q, walk)
        # Then, if we are jumping, set our z velocity to be the jump speed
        # and turn off the jump (we only jump once).
        if (jump):
            vel[2] = Speed["jump"]
            player_jump(False)

    # Save our velocity for next time
    Player["vel"] = vel

    # If we aren't moving, there's nothing to do.
    if (vel == [0, 0, 0]):
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
        player_die()

    # Save our new position.
    Player["pos"] = pos


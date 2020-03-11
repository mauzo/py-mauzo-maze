# camera.py - Camera
# Functions for manipulating the camera.

from    math        import fmod
from    OpenGL.GL   import *

# This dict has information about the camera. The camera moves with the
# player but has its own direction. Most of these values are just dummies
# which will be set up by camera_init.
# This must appear before the imports below because player.py uses it.
Camera = {
    # How far away from the player are we?
    "offset":   8,
    ## The current position of the camera.
    #"pos":      [0, 0, 0],
    ## Does our position need updating?
    #"moved":    True,
    # The current camera angle, horizontal and vertical.
    "angle":    [70, -10],
    # The current pan speeds
    "pan":      [0, 0],
    # The horizontal camera angle as a quaternion
    "walk_quat": [0, 0, 0, 0],
}

from    .player     import Player
from    .vectors    import *

# This is the speed the camera pans at, in degrees/second.
CAMERA_PAN  = 60

# Change the camera pan speed
def camera_pan (v):
    Camera["pan"][0] += v[0] * CAMERA_PAN
    Camera["pan"][1] += v[1] * CAMERA_PAN

def camera_init ():
    camera_update_walk_quat()
    #camera_do_move()

# Keep walk_quat up to date with the walk direction
def camera_update_walk_quat ():
    angle = Camera["angle"]
    Camera["walk_quat"] = quat_rotate_about(angle[0], [0, 0, 1])
    #print("Camera angle", angle, "quat", Camera["walk_quat"])

# Update the camera angle if we are panning.
def camera_do_pan (dt):
    pan     = Camera["pan"]
    if (pan == [0, 0]):
        return

    # Multiply the pan speed by the time step so we always pan at the
    # same speed.
    delta   = [x * dt for x in pan]
    angle   = Camera["angle"]

    # This fmod() function divides by 360 and takes the remainder.
    # This makes sure we are always between 0 and 360 degrees.
    # We subtract delta[0] because angles are measured CCW but we want
    # a +ve pan to turn us right. Otherwise it's confusing.
    horiz = fmod(angle[0] - delta[0], 360)
    if (horiz < 0):
        horiz += 360
    
    vert = angle[1] + delta[1]
    if (vert > 90):
        vert = 90
    if (vert < -90):
        vert = -90

    Camera["angle"]     = [horiz, vert]
    camera_update_walk_quat()

# Update the camera
def camera_physics (dt):
    camera_do_pan(dt)

# Position the camera based on the player's current position. We put
# the camera 1 unit above the player's position.
def render_camera():
    pos     = Player["pos"]
    off     = Camera["offset"]
    angle   = Camera["angle"]
    
    # Clear the previous camera position
    glLoadIdentity()
    # Annoyingly, the camera starts pointing down (-Z).
    # Rotate so we are pointing down +X with +Z upwards.
    glRotatef(90, 0, 0, 1)
    glRotatef(90, 0, 1, 0)

    # Set the new camera position for this frame. Everything has to be
    # done backwards because we are moving the world rather than moving
    # the camera. This is why we rotate before we translate rather than
    # the other way round.
    
    # Back off from the player position.
    glTranslatef(off, 0, 0)
    # Vertical rotation. We are pointing down +X so we would expect a
    # CCW rotation about -Y to make +ve angles turn upwards, but as
    # everthing is backwards we need to turn the other way.
    glRotatef(angle[1], 0, 1, 0)
    # Horizontal rotation. Again we rotate about -Z rather than +Z.
    glRotatef(angle[0], 0, 0, -1)
    # Move to the camera position. These need to be negative because we
    # are moving the world rather than moving the camera.
    glTranslatef(-pos[0], -pos[1], -pos[2])


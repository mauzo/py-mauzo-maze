# camera.py - Camera
# Functions for manipulating the camera.

import  glm
from    glm         import degrees, radians, vec2, vec3, vec4
from    math        import fmod
from    OpenGL.GL   import *

# This is the speed the camera pans at, in radians/second.
CAMERA_PAN  = radians(60)

HALFPI      = glm.half_pi()
TWOPI       = glm.two_pi()

# This object has information about the camera. The camera moves with the
# player but has its own direction.
class Camera:
    # The attributes this object can have
    __slots__ = [
        # The app we are running in
        "app",
        # How far away from the player are we?
        "offset",
        # The current camera angle, horizontal and vertical.
        "angle",
        # The current pan speeds
        "panning",
        # The player object
        "player",
    ]

    # This is called automatically to set up the object
    def __init__ (self, app, player):
        self.offset     = 8
        self.angle      = vec2(radians(70), radians(-10))
        self.panning    = vec2(0, 0)
        self.player     = player

    def init (self):
        # Make sure the player is facing the right way
        self.update_player_face()

    # Change the camera pan speed
    def pan (self, v):
        self.panning += v * CAMERA_PAN

    # Keep player up to date with the walk direction
    def update_player_face (self):
        self.player.face(degrees(self.angle.x))

    # Update the camera angle if we are panning.
    def do_pan (self, dt):
        if self.panning == vec2(0, 0):
            return

        # Multiply the pan speed by the time step so we always pan at the
        # same speed.
        delta   = dt * self.panning
        angle   = self.angle

        # This fmod() function divides by 360 and takes the remainder.
        # This makes sure we are always between 0 and 360 degrees.
        # We subtract delta[0] because angles are measured CCW but we want
        # a +ve pan to turn us right. Otherwise it's confusing.
        horiz = fmod(angle.x - delta.x, TWOPI)
        if (horiz < 0):
            horiz += TWOPI
        
        vert = glm.clamp(angle.y + delta.y, -HALFPI, HALFPI)

        self.angle = vec2(horiz, vert)
        self.update_player_face()

    # Update the camera
    def physics (self, dt):
        self.do_pan(dt)

    # Position the camera based on the player's current position. We put
    # the camera 1 unit above the player's position.
    def render (self):
        pos     = self.player.pos
        angle   = self.angle
        
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
        glTranslatef(self.offset, 0, 0)
        # Vertical rotation. We are pointing down +X so we would expect a
        # CCW rotation about -Y to make +ve angles turn upwards, but as
        # everthing is backwards we need to turn the other way.
        glRotatef(degrees(angle[1]), 0, 1, 0)
        # Horizontal rotation. Again we rotate about -Z rather than +Z.
        glRotatef(degrees(angle[0]), 0, 0, -1)
        # Move to the camera position. These need to be negative because we
        # are moving the world rather than moving the camera.
        glTranslatef(-pos[0], -pos[1], -pos[2])


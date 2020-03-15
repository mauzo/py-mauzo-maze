# The Camera class from learnopengl.com translated to Python

import  glm
from    glm     import vec3, radians
from    math    import cos, sin

FORWARD     = 1
BACKWARD    = 2
LEFT        = 3
RIGHT       = 4

class Camera:
    __slots__ = [
        "position", "front", "up", "right", "world_up",
        "yaw", "pitch", 
        "speed", "sensitivity", "zoom",
    ]

    def __init__ (self,
        pos     = vec3(0, 0, 0),
        up      = vec3(0, 1, 0), 
        yaw     = -90,
        pitch   = 0,
    ):
        self.position   = pos
        self.world_up   = up
        self.yaw        = yaw
        self.pitch      = pitch

        self.speed          = 2.5
        self.sensitivity    = 0.1
        self.zoom           = 45

        self.update()

    def get_view_matrix (self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def process_keyboard (self, direction, dt):
        velocity    = self.speed * dt

        if direction == FORWARD:
            self.position += self.front * velocity
        elif direction == BACKWARD:
            self.position -= self.front * velocity
        elif direction == LEFT:
            self.position -= self.right * velocity
        elif direction == RIGHT:
            self.position += self.right * velocity

    def process_mouse (self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw    += xoffset
        self.pitch  += yoffset

        if constrain_pitch:
            self.pitch = glm.clamp(self.pitch, -89, 89)

        self.update()

    def process_scroll (self, yoffset):
        self.zoom = glm.clamp(self.zoom - yoffset, 1, 45)

    def update (self):
        yaw     = radians(self.yaw)
        pitch   = radians(self.pitch)

        front   = vec3()
        front.x = cos(yaw) * cos(pitch)
        front.y = sin(pitch)
        front.z = sin(yaw) * cos(pitch)

        self.front  = glm.normalize(front)
        self.right  = glm.normalize(glm.cross(self.front, self.world_up))
        self.up     = glm.normalize(glm.cross(self.right, self.front))


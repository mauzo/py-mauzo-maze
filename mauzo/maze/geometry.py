# geometry.py - geometry utility function

import  glm
from    glm     import mat3, mat4, quat, radians, vec2, vec3, vec4

# Given a plane x = p + sa + tb return the vec4(A,B,C,D) where
# vec3(A,B,C) is normal to the plane and Ax + By + Cz + D = 0 is an
# equation of the plane. 
def plane_from_vectors (p, a, b):
    n   = glm.normalize(glm.cross(a, b))
    d   = -glm.dot(n, p)
    return vec4(n, d)

# Given a plane represented by its normal, project a vector onto that
# plane. This assumes planes/vectors through the origin.
# XXX I think there must be an easier algorithm here...
def project_onto_plane (p, v):
    r   = glm.normalize(glm.cross(p, v))
    q   = glm.cross(r, p)
    w   = glm.dot(v, q) * q

    return w

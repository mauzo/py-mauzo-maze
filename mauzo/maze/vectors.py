# Vector operations

# These are mathematical operations on 3D vectors. Maybe we should be using
# a library instead? (numpy will not work as-is with 4-vectors, since it
# doesn't handle the w-coordinate specially.)

# Vectors are represented as 3-element lists. Currently passing in a 3-element
# tuple will work as well.

# NOTE: despite the documentation, it is easier to consider GL matrices
# as being in row-major order, with successive operations pre-
# multiplied, and the matrix pre-multiplied to a column vector.
# That is, given a translation T, a rotation R and a vector v calling
#       glTranslate(...)
#       glRotate(...)
# will give R @ T @ v as the transformed vector. This matches the usual
# conventions, and is equivalent to post-multiplying column-major
# matrices as the GL documentation describes.

from    math        import cos, sin, sqrt, radians
import  numpy       as np

# Add two vectors
def vec_add (a, b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]

# Negate a vector
def vec_neg (v):
    return [-v[0], -v[1], -v[2]]

# Subtract b from a
def vec_subtract (a, b):
    return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

# Multiply a vector by a number
def vec_mul (v, s):
    return [v[0]*s, v[1]*s, v[2]*s]

# Find the length of a vector
def vec_norm (v):
    return sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

# Find a vector of length 1 in the same direction as v
def vec_unit (v):
    n = vec_norm(v)
    return [v[0]/n, v[1]/n, v[2]/n]

# Vector dot product
def vec_dot (a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

# Vector cross product
def vec_cross (a, b):
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]

# Quaternions are an extension of the complex numbers to use 3
# imaginary units i,j,k. They can be used to represent 3D rotations.
# Quaternions are represented by 4-element lists [i, j, k, 1].
# XXX Should I use bivectors instead?

# Make a quaternion to rotate by 'by' around v
def quat_rotate_about (by, v):
    angle   = radians(by/2.0)
    s       = sin(angle)
    c       = cos(angle)
    return [v[0]*s, v[1]*s, v[2]*s, c]

# Make a quaternion to rotate from u to v
def quat_rotate_from_to (u, v):
    c   = sqrt(2.0 * (1.0 + vec_dot(u, v)))
    w   = vec_mul(vec_cross(u, v), 1.0/c)
    
    return [*w, c/2.0]

# Apply a quaternion rotation to a vector
def quat_apply (q, v):
    x = q[3]*v[0] + q[1]*v[2] - q[2]*v[1]
    y = q[3]*v[1] + q[2]*v[0] - q[0]*v[2]
    z = q[3]*v[2] + q[0]*v[1] - q[1]*v[0]
    w = q[0]*v[0] + q[1]*v[1] + q[2]*v[2]

    return [w*q[0] + x*q[3] - y*q[2] + z*q[1],
            w*q[1] + y*q[3] - z*q[0] + x*q[2],
            w*q[2] + z*q[3] - x*q[1] + y*q[0]]

# Multiply two quaternions (apply the rotations one after the other)
def quat_mul (q0, q1):
    return [q0[3]*q1[0] + q0[0]*q1[3] + q0[1]*q1[2] - q0[2]*q1[1],
            q0[3]*q1[1] + q0[1]*q1[3] + q0[2]*q1[0] - q0[0]*q1[2],
            q0[3]*q1[2] + q0[2]*q1[3] + q0[0]*q1[1] - q0[1]*q1[0],
            q0[3]*q1[3] - q0[0]*q1[0] - q0[1]*q1[1] - q0[2]*q1[2]]

# Convert a quaternion into a matrix which represents the same rotation.
# Optionally include a translation vector too.
# Returns the matrix as a ndarray for passing to GL.
def quat_to_matrix (q, v):
    if (v is None):
        v = (0.0, 0.0, 0.0)
    qx2     = q[0] + q[0];
    qy2     = q[1] + q[1];
    qz2     = q[2] + q[2];
    qxqx2   = q[0] * qx2;
    qxqy2   = q[0] * qy2;
    qxqz2   = q[0] * qz2;
    qxqw2   = q[3] * qx2;
    qyqy2   = q[1] * qy2;
    qyqz2   = q[1] * qz2;
    qyqw2   = q[3] * qy2;
    qzqz2   = q[2] * qz2;
    qzqw2   = q[3] * qz2;

    # XXX This does a pre-multiply by the translation. Is it easy to
    # do a post-multiply instead, for camera matrices?
    return np.array([
        [(1.0 - qyqy2) - qzqz2, qxqy2 + qzqw2, qxqz2 - qyqw2, 0.0],
        [qxqy2 - qzqw2, (1.0 - qxqx2) - qzqz2, qyqz2 + qxqw2, 0.0],
        [qxqz2 + qyqw2, qyqz2 - qxqw2, (1.0 - qxqx2) - qyqy2, 0.0],
            # q11*u1+q12*u2+q13*u3+v1, ...
        [v[0], v[1], v[2], 1.0],
    ], dtype=np.float)


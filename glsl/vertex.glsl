#version 330 core

in      vec3    b_pos;
uniform float   u_offset;
out     vec3    v_color;

void main ()
{
    gl_Position = vec4(b_pos.x + u_offset, b_pos.y, b_pos.z, 1.0);
    v_color     = b_pos;
}

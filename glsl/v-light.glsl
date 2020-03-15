#version 330 core

in      vec3    b_pos;

uniform mat4    u_proj;
uniform mat4    u_view;
uniform mat4    u_model;

void main ()
{
    gl_Position = u_proj * u_view * u_model * vec4(b_pos, 1.0);
}

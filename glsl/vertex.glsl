#version 330 core

in      vec3    b_pos;
in      vec3    b_color;
in      vec2    b_tex;

out     vec3    v_color;
out     vec2    v_tex;

uniform mat4    u_proj;
uniform mat4    u_view;
uniform mat4    u_model;

void main ()
{
    gl_Position = u_proj * u_view * u_model * vec4(b_pos, 1.0);
    v_color     = b_color;
    v_tex       = b_tex;
}

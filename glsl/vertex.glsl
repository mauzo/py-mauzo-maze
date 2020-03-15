#version 330 core

in      vec3    b_pos;
in      vec3    b_color;
in      vec2    b_tex;

out     vec3    v_color;
out     vec2    v_tex;

void main ()
{
    gl_Position = vec4(b_pos.x, b_pos.y, b_pos.z, 1.0);
    v_color     = b_color;
    v_tex       = b_tex;
}

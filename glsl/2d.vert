#version 130

in      vec2    b_pos;
in      vec2    b_tex;

out     vec3    v_pos;
out     vec2    v_tex;

uniform mat4    u_proj;
uniform mat4    u_model;

void main ()
{
    vec4 pos4   = u_model * vec4(b_pos, 0.0, 1.0);

    gl_Position = u_proj * pos4;
    v_pos       = vec3(pos4);
    v_tex       = b_tex;
}

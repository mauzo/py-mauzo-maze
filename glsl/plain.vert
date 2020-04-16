#version 130

in      vec3    b_pos;
in      vec3    b_normal;
in      vec2    b_tex;

out     vec3    v_pos;
out     vec3    v_normal;
out     vec3    v_view_dir;
out     vec2    v_tex;

uniform mat4    u_proj;
uniform mat4    u_view;
uniform mat4    u_model;
uniform mat3    u_normal_matrix;
uniform vec3    u_view_pos;

void main ()
{
    vec4 pos4   = u_model * vec4(b_pos, 1.0);

    gl_Position = u_proj * u_view * pos4;
    v_pos       = vec3(pos4);
    v_normal    = normalize(u_normal_matrix * b_normal);
    v_view_dir  = normalize(u_view_pos - v_pos);
    v_tex       = b_tex;
}

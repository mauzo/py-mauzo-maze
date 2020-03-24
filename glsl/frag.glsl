#version 330 core

in      vec3    v_color;
in      vec2    v_tex;

out     vec4    f_color;

uniform sampler2D   u_basetex;
uniform sampler2D   u_overlaytex;

void main ()
{
    f_color = mix(
        texture(u_basetex, v_tex), 
        texture(u_overlaytex, v_tex), 
        0.2
    );
}

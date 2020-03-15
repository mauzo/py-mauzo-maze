#version 330 core

out     vec4    f_color;

uniform vec3    u_obj_color;
uniform vec3    u_light_color;

void main ()
{
    f_color = vec4(u_light_color * u_obj_color, 1.0);
}

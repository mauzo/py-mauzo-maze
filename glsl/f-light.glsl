#version 130

out     vec4    f_color;

uniform vec3    u_color;

void main ()
{
    f_color = vec4(u_color, 1.0);
}

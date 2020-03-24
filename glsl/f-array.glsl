#version 330 core

struct Light {
    float   red;
    float   green;
    float   blue;
};

out     vec4    f_color;

uniform float   u_color[3];
uniform Light   u_lights[2];

void main ()
{
    f_color = vec4(u_color[0] + u_lights[0].red + u_lights[1].red,
                    u_color[1] + u_lights[0].green + u_lights[1].green,
                    u_color[2] + u_lights[0].blue + u_lights[1].blue,
                    1.0);
}

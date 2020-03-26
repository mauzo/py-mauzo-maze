#version 130

struct Material {
    vec3        diffuse;
    float       specular;
    float       shininess;
};

out     vec4    f_color;

uniform Material    u_material;

void 
main ()
{
    f_color         = vec4(1.0, 1.0, 1.0, 1.0);
}

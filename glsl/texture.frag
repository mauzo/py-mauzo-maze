#version 130

struct Material {
    vec3        diffuse;
    float       specular;
    float       shininess;
};

struct Textures {
    sampler2D   diffuse;
    sampler2D   specular;
};

struct LightParams {
    vec3    position;
    vec3    normal;
    vec3    view_dir;

    vec3    color;
    float   hilite;
    float   shininess;
};

in      vec3    v_pos;
in      vec3    v_normal;
in      vec2    v_tex;

out     vec4    f_color;

uniform vec3        u_view_pos;
uniform Material    u_material;
uniform Textures    u_textures;

void 
main ()
{
    // fragment parameters
    LightParams p;
    p.position  = v_pos;
    p.normal    = normalize(v_normal);
    p.view_dir  = normalize(u_view_pos - v_pos);
    p.color     = texture(u_material.diffuse, v_tex).rgb;
    p.hilite    = texture(u_material.specular, v_tex).a;
    p.shininess = u_material.shininess;

    // perform lighting
}

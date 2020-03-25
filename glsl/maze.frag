#version 130

struct Material {
    vec3        diffuse;
    float       specular;
    float       shininess;
};

struct LightParams {
    vec3    position;
    vec3    normal;
    vec3    view_dir;

    vec3    color;
    float   hilite;
    float   shininess;
};

struct LightColor {
    vec3    ambient;
    vec3    diffuse;
    vec3    specular;
};

struct DirLight {
    vec3        direction;
    LightColor  color;
};

in      vec3    v_pos;
in      vec3    v_normal;
in      vec2    v_tex;

out     vec4    f_color;

uniform vec3        u_view_pos;

uniform Material    u_material;
uniform DirLight    u_sun;

LightColor  light_basic         (LightColor l, LightParams p, vec3 light_dir);
vec3        light_directional   (DirLight light, LightParams p);

LightColor
light_basic (LightColor l, LightParams p, vec3 light_dir)
{
    LightColor  res;

    // ambient
    res.ambient         = l.ambient * p.color;

    // diffuse
    float   diff        = max(dot(p.normal, light_dir), 0.0);
    res.diffuse         = l.diffuse * diff * p.color;

    // specular
    vec3    reflect_dir = reflect(-light_dir, p.normal);
    float   spec_base   = max(dot(p.view_dir, reflect_dir), 0.0);
    float   spec        = pow(spec_base, p.shininess);
    res.specular        = l.specular * spec * p.hilite;

    return res;
}

vec3 
light_directional (DirLight light, LightParams p)
{
    vec3        light_dir   = normalize(-light.direction);
    LightColor  l           = light_basic(light.color, p, light_dir);

    return l.ambient + l.diffuse + l.specular;
}

void 
main ()
{
    // fragment parameters
    LightParams p;
    p.position  = v_pos;
    p.normal    = normalize(v_normal);
    p.view_dir  = normalize(u_view_pos - v_pos);
    p.color     = u_material.diffuse;
    p.hilite    = u_material.specular;
    p.shininess = u_material.shininess;

    // directional light
    vec3    result  = light_directional(u_sun, p);

    f_color         = vec4(result, 1.0);
}

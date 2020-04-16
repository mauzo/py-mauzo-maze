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
    vec3    light_dir;

    Material    material;
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

in      vec3        v_pos;
in      vec3        v_normal;
in      vec3        v_view_dir;

out     vec4        f_color;

uniform Material    u_material;
uniform DirLight    u_sun;

LightColor  light_basic         (LightColor l, LightParams p);
vec3        light_directional   (DirLight light, LightParams p);

LightColor
light_basic (LightColor l, LightParams p)
{
    LightColor  res;
    Material    m   = p.material;

    // ambient
    res.ambient         = l.ambient * m.diffuse;

    // diffuse
    float   diff        = max(dot(p.normal, p.light_dir), 0.0);
    res.diffuse         = l.diffuse * diff * m.diffuse;

    // specular
    vec3    reflect_dir = reflect(-p.light_dir, p.normal);
    float   spec_base   = max(dot(p.view_dir, reflect_dir), 0.0);
    float   spec        = pow(spec_base, m.shininess);
    res.specular        = l.specular * spec * m.specular;

    return res;
}

vec3 
light_directional (DirLight light, LightParams p)
{
    p.light_dir     = normalize(-light.direction);
    LightColor  l   = light_basic(light.color, p);

    return l.ambient + l.diffuse + l.specular;
}

void 
main ()
{
    LightParams p;
    p.position      = v_pos;
    p.normal        = v_normal;
    p.view_dir      = v_view_dir;
    p.material      = u_material;

    // directional light
    vec3    result  = light_directional(u_sun, p);

    f_color         = vec4(result, 1.0);
}

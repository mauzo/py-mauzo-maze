#version 330 core

struct Material {
    sampler2D   diffuse;
    sampler2D   specular;
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

struct PointLight {
    vec3        position;

    float       linear;
    float       quadratic;

    LightColor  color;
};

struct SpotLight {
    vec3        position;
    vec3        direction;
    float       cutoff;
    float       softness;

    LightColor  color;
};

in      vec3    v_pos;
in      vec3    v_normal;
in      vec2    v_tex;

out     vec4    f_color;

uniform mat3        u_normal_matrix;
uniform vec3        u_view_pos;

#define POINT_LIGHTS 4

uniform Material    u_material;
uniform DirLight    u_sun;
uniform PointLight  u_light[POINT_LIGHTS];
uniform SpotLight   u_spot;

LightColor  light_basic         (LightColor l, LightParams p, vec3 light_dir);
vec3        light_directional   (DirLight light, LightParams p);
vec3        light_positional    (PointLight light, LightParams p);
vec3        light_spot          (SpotLight light, LightParams p);

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

vec3
light_positional (PointLight light, LightParams p)
{
    // vectors
    vec3    light_off   = light.position - p.position;
    vec3    light_dir   = normalize(light_off);
    float   distance    = length(light_off);

    // basic light
    LightColor  l       = light_basic(light.color, p, light_dir);

    // attenuation
    float   attenuation = 1.0 / (1.0 +
        light.linear * distance +
        light.quadratic * (distance * distance));

    return (l.ambient + l.diffuse + l.specular) * attenuation;
}

//vec3
//light_spot (SpotLight light, LightParams p)
//{
    // XXX incomplete
    // spot
    //float   theta       = dot(light_dir, normalize(-u_light.direction));
    //float   spot_cone   = (theta - u_light.cutoff) / u_light.softness;
    //float   spot        = clamp(spot_cone, 0, 1);

    //return vec3(1.0);
//}

void 
main ()
{
    // fragment parameters
    LightParams p;
    p.position  = v_pos;
    p.normal    = normalize(u_normal_matrix * v_normal);
    p.view_dir  = normalize(u_view_pos - v_pos);
    p.color     = texture(u_material.diffuse, v_tex).rgb;
    p.hilite    = texture(u_material.specular, v_tex).a;
    p.shininess = u_material.shininess;

    // directional light
    vec3    result  = light_directional(u_sun, p);
    
    int i;
    for (i = 0; i < POINT_LIGHTS; i++)
        result      += light_positional(u_light[i], p);

    f_color         = vec4(result, 1.0);
}

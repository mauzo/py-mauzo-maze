#version 330 core
// vi:set syn=c:

struct Material {
    sampler2D   diffuse;
    sampler2D   specular;
    sampler2D   magic;
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

struct MagicLight {
    vec3        position;
    vec3        direction;
    float       cutoff;
    float       softness;
    float       limit;
};

in      vec3    v_pos;
in      vec3    v_normal;
in      vec2    v_tex;

out     vec4    f_color;

uniform mat3        u_normal_matrix;
uniform vec3        u_view_pos;
uniform float       u_now;

#define POINT_LIGHTS 4

uniform Material    u_material;
uniform DirLight    u_sun;
uniform PointLight  u_light[POINT_LIGHTS];
//uniform SpotLight   u_spot;
uniform MagicLight  u_magic;

LightColor  light_basic         (LightColor l, LightParams p, vec3 light_dir);
vec3        light_directional   (DirLight light, LightParams p);
vec3        light_positional    (PointLight light, LightParams p);
vec3        light_spot          (SpotLight light, LightParams p);
vec3        light_magic         (MagicLight light, LightParams p, vec3 m);

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

vec3
light_spot (SpotLight light, LightParams p)
{
    vec3        light_dir   = normalize(light.position - p.position);
    LightColor  l           = light_basic(light.color, p, light_dir);

    // spot cone
    float   theta       = dot(light_dir, normalize(-light.direction));
    float   spot_cone   = (theta - light.cutoff) / light.softness;
    float   spot        = clamp(spot_cone, 0, 1);

    return l.ambient + (l.diffuse + l.specular) * spot;
}

vec3
light_magic (MagicLight light, LightParams p, vec3 m)
{
    vec3    light_off   = light.position - p.position;
    vec3    light_dir   = normalize(light_off);
    float   distance    = length(light_off);

    float   theta       = dot(light_dir, normalize(-light.direction));
    float   spot_cone   = (theta - light.cutoff) / light.softness;
    float   spot_fade   = 1.0 - distance / light.limit;
    float   spot        = clamp(spot_cone, 0, 1) * clamp(spot_fade, 0, 1);

    return m * spot * float(p.hilite == 0);
}

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
    
    // point lights
    int i;
    for (i = 0; i < POINT_LIGHTS; i++)
        result      += light_positional(u_light[i], p);

    // spotlight
    //result  += light_spot(u_spot, p);

    // magic light
    vec2 magic_tex  = v_tex + vec2(0, u_now/4);
    vec3 magic      = texture(u_material.magic, magic_tex).rgb;
    result          += light_magic(u_magic, p, magic);

    f_color         = vec4(result, 1.0);
}

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


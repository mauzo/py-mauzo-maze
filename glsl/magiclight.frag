struct MagicLight {
    vec3        position;
    vec3        direction;
    float       cutoff;
    float       softness;
    float       limit;
};

vec3        light_magic         (MagicLight light, LightParams p, vec3 m);

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


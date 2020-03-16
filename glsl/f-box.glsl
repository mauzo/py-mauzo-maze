#version 330 core

struct Material {
    sampler2D   diffuse;
    sampler2D   specular;
    float       shininess;
};

struct Light {
    vec3    position;
    vec3    direction;
    float   cutoff;
    float   softness;

    vec3    ambient;
    vec3    diffuse;
    vec3    specular;

    float   linear;
    float   quadratic;
};

in      vec3    v_pos;
in      vec3    v_normal;
in      vec2    v_tex;

out     vec4    f_color;

uniform mat3        u_normal_matrix;
uniform Light       u_light;
uniform Material    u_material;
uniform vec3        u_view_pos;

void main ()
{
    // vectors
    vec3    norm        = normalize(u_normal_matrix * v_normal);
    vec3    light_off   = u_light.position - v_pos;
    vec3    light_dir   = normalize(light_off);

    // attenuation
    float   distance    = length(light_off);
    float   attenuation = 1.0 / (1.0 +
        u_light.linear * distance +
        u_light.quadratic * (distance * distance));

    // texture lookup
    vec3    color       = texture(u_material.diffuse, v_tex).rgb;
    float   hilite      = texture(u_material.specular, v_tex).a;

    // ambient
    vec3    ambient     = u_light.ambient * color;

    // diffuse
    float   diff        = max(dot(norm, light_dir), 0.0);
    vec3    diffuse     = u_light.diffuse * diff * color;

    // specular
    vec3    view_dir    = normalize(u_view_pos - v_pos);
    vec3    reflect_dir = reflect(-light_dir, norm);
    float   spec_base   = max(dot(view_dir, reflect_dir), 0.0);
    float   spec        = pow(spec_base, u_material.shininess);
    vec3    specular    = u_light.specular * spec * hilite;

    // spot
    float   theta       = dot(light_dir, normalize(-u_light.direction));
    float   spot_cone   = (theta - u_light.cutoff) / u_light.softness;
    float   spot        = clamp(spot_cone, 0, 1);

    vec3    direct      = diffuse + specular;
    vec3    light       = ambient + direct  * spot * attenuation;
    f_color             = vec4(light, 1.0);
}

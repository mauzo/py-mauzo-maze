#version 330 core

struct Material {
    sampler2D   diffuse;
    sampler2D   specular;
    float       shininess;
};

struct Light {
    vec3    direction;
    vec3    ambient;
    vec3    diffuse;
    vec3    specular;
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
    vec3    norm        = normalize(u_normal_matrix * v_normal);
    vec3    light_dir   = normalize(-u_light.direction);

    vec3    color       = texture(u_material.diffuse, v_tex).rgb;
    float   hilite      = texture(u_material.specular, v_tex).a;

    vec3    ambient     = u_light.ambient * color;

    float   diff        = max(dot(norm, light_dir), 0.0);
    vec3    diffuse     = u_light.diffuse * diff * color;

    vec3    view_dir    = normalize(u_view_pos - v_pos);
    vec3    reflect_dir = reflect(-light_dir, norm);
    float   spec_base   = max(dot(view_dir, reflect_dir), 0.0);
    float   spec        = pow(spec_base, u_material.shininess);
    vec3    specular    = u_light.specular * spec * hilite;

    vec3    result  = ambient + diffuse + specular;
    f_color         = vec4(result, 1.0);
}

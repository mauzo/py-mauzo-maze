#version 330 core

in      vec3    v_pos;
in      vec3    v_normal;

out     vec4    f_color;

uniform vec3    u_obj_color;
uniform vec3    u_light_color;
uniform vec3    u_light_pos;

void main ()
{
    float   ambient_strength    = 0.1;
    vec3    ambient             = ambient_strength * u_light_color;

    vec3    norm        = normalize(v_normal);
    vec3    light_dir   = normalize(u_light_pos - v_pos);
    float   diff        = max(dot(norm, light_dir), 0.0);
    vec3    diffuse     = diff * u_light_color;

    vec3    result  = (ambient + diffuse) * u_obj_color;

    f_color = vec4(result, 1.0);
}

#version 330 core

in      vec3    v_pos;
in      vec3    v_normal;

out     vec4    f_color;

uniform vec3    u_obj_color;
uniform vec3    u_light_color;
uniform vec3    u_light_pos;
uniform vec3    u_view_pos;

void main ()
{
    float   ambient_str = 0.1;
    vec3    ambient     = ambient_str * u_light_color;

    vec3    norm        = normalize(v_normal);
    vec3    light_dir   = normalize(u_light_pos - v_pos);
    float   diff        = max(dot(norm, light_dir), 0.0);
    vec3    diffuse     = diff * u_light_color;

    float   spec_str    = 0.5;
    vec3    view_dir    = normalize(u_view_pos - v_pos);
    vec3    reflect_dir = reflect(-light_dir, norm);
    float   spec        = pow(max(dot(view_dir, reflect_dir), 0.0), 32);
    vec3    specular    = spec_str * spec * u_light_color;

    vec3    result  = (ambient + diffuse + specular) * u_obj_color;

    f_color = vec4(result, 1.0);
}

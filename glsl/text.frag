#version 130

in      vec3    v_pos;
in      vec2    v_tex;

out     vec4    f_color;

uniform vec4        u_color;
uniform sampler2D   u_mask;

void 
main ()
{
    float mask  = texture(u_mask, v_tex).a;
    f_color     = vec4(u_color.rgb, u_color.a * mask);
}

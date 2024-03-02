#version 410 core

layout (points) in;
layout (line_strip, max_vertices = 2) out;

uniform mat4 m_projection;
uniform mat4 m_model;
uniform mat4 m_view;

in VS_OUT {
    //vec3 normal;
    vec4 proj_normal_1;
    vec4 proj_normal_2;
    //vec3 color;
} gs_in[];

//out GS_OUT {
//    vec3 normal;
//    vec3 color;
//} gs_out;

void main()
{
    //gs_out.normal = gs_in[0].proj_normal;
    //gs_out.color = gs_in[0].color;

    //gl_Position = vec4(gl_in[0].gl_Position);
    gl_Position = gs_in[0].proj_normal_1;
    EmitVertex();
    gl_Position = gs_in[0].proj_normal_2;
    EmitVertex();
    EndPrimitive();

    //gl_Position = vec4(gs_in[0].proj_normal_2, 1.0);
    //EmitVertex();
    //EndPrimitive();
}

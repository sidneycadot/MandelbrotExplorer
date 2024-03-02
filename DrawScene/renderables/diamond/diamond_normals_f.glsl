
#version 410 core

uniform mat4 m_projection;
uniform mat4 m_model;
uniform mat4 m_view;

layout(location = 0) out vec4 fragment_color;

//in GS_OUT {
//    vec3 normal;
//    vec3 color;
//} fs_in;

void main()
{
    fragment_color = vec4(1.0, 1.0, 0.0, 1.0);
}

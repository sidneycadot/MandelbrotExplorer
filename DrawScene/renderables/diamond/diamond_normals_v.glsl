
#version 410 core

layout(location = 0) in vec3 a_vertex;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec3 a_color;

uniform mat4 m_projection;
uniform mat4 m_model;
uniform mat4 m_view;

uniform uint cells_per_dimension;

const float UNIT_CELL_SIZE = 4.0;

out VS_OUT {
    vec4 proj_normal_1;
    vec4 proj_normal_2;
} vs_out;

void main()
{
    uint iz = gl_InstanceID;
    uint ix = iz % cells_per_dimension; iz /= cells_per_dimension;
    uint iy = iz % cells_per_dimension; iz /= cells_per_dimension;

    vec3 offset = UNIT_CELL_SIZE * (vec3(ix, iy, iz) - 0.5 * cells_per_dimension);

    mat4 mv  = m_view * m_model;
    mat4 mvp = m_projection * mv;

    gl_Position          = mvp * vec4(a_vertex + offset, 1.0);
    vs_out.proj_normal_1 = mvp * vec4(a_vertex + offset + 0.0 * a_normal, 1.0);
    vs_out.proj_normal_2 = mvp * vec4(a_vertex + offset + 0.2 * a_normal, 1.0);

    //vs_out.normal = normalize((transpose(inverse(m_view * m_model)) * vec4(a_normal, 0.0)).xyz);
    //vs_out.color = a_color;
}

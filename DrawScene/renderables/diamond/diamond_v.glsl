
#version 410 core

layout(location = 0) in vec3 a_vertex;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec3 a_color;

uniform mat4 m_projection;
uniform mat4 m_model;
uniform mat4 m_view;

uniform uint cells_per_dimension;

out vec3 v_normal;
out vec3 v_color;

void main()
{
    uint iz = gl_InstanceID;
    uint ix = iz % cells_per_dimension; iz /= cells_per_dimension;
    uint iy = iz % cells_per_dimension; iz /= cells_per_dimension;

    vec3 offset = 4 * (vec3(ix, iy, iz)  - 0.5 * cells_per_dimension);

    //vec3 offset = vec3(0, 0, 0);

    mat4 mvp = m_projection * m_view * m_model;

    gl_Position = mvp * vec4(a_vertex + offset, 1.0);

    v_normal = normalize((transpose(inverse(m_view * m_model)) * vec4(a_normal, 0.0)).xyz);
    v_color = a_color;
}

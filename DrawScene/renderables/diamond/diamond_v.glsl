
#version 410 core

layout(location = 0) in vec3 a_vertex;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec3 a_color;

uniform mat4 m_projection;
uniform mat4 m_model;
uniform mat4 m_view;
uniform uint cells_per_dimension;

out VS_OUT {
    vec3 mv_surface;
    vec3 mv_normal;
} vs_out;

vec3 vec4_to_vec3(vec4 v)
{
    return v.xyz / v.w;
}

const float UNIT_CELL_SIZE = 4.0;

void main()
{
    uint iz = gl_InstanceID;
    uint ix = iz % cells_per_dimension; iz /= cells_per_dimension;
    uint iy = iz % cells_per_dimension; iz /= cells_per_dimension;

    vec3 offset = UNIT_CELL_SIZE * (vec3(ix, iy, iz) - 0.5 * cells_per_dimension);

    mat4 mv  = m_view * m_model;
    mat4 mvp = m_projection * mv;

    gl_Position = mvp * vec4(a_vertex + offset, 1.0);

    vs_out.mv_surface = vec4_to_vec3(mv * vec4(a_vertex + offset, 1.0));
    vs_out.mv_normal = normalize((transpose(inverse(mv)) * vec4(a_normal, 0.0)).xyz);
}

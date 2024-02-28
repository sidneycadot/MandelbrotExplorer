
#version 410 core

layout(location = 0) in vec3 a_vertex;
layout(location = 1) in vec3 a_color;

uniform mat4 mvp;

out vec3 v_color;

void main()
{
    uint per_dim = 8;

    uint iz = gl_InstanceID;
    uint ix = iz % per_dim; iz /= per_dim;
    uint iy = iz % per_dim; iz /= per_dim;

    //float center = 0.5 * per_dim;

    vec3 offset = 4.0 * vec3(ix - 0.5, iy - 0.5, iz - 0.5) - 0.5*(per_dim - 1) * vec3(4, 4, 4);

    gl_Position = mvp * vec4(a_vertex + offset, 1.0);

    v_color = a_color;
}

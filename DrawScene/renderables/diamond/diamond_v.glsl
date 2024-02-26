
#version 410 core

layout(location = 0) in vec3 a_vertex;
layout(location = 1) in vec3 a_color;

uniform mat4 mvp;

out vec3 v_color;

void main()
{
    // Make 4D vertex from 3D value.
    uint iz = gl_InstanceID;
    uint ix = iz % 100; iz /= 100;
    uint iy = iz % 100; iz /= 100;
    iz = iz % 100;

    vec3 offset = (vec3(ix, iy, iz) - 49.5) * 23.3;
    gl_Position = mvp * vec4(a_vertex + offset, 1.0);

    v_color = a_color;
}

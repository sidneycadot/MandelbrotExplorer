
#version 410 core

layout(location = 0) in vec3 a_vertex;
layout(location = 1) in vec3 a_color;

uniform mat4 mvp;

out vec3 v_color;

void main()
{
    // Make 4D vertex from 3D value.
    gl_Position = mvp * vec4(a_vertex, 1.0);

    v_color = a_color;
}

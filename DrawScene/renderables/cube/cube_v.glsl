
#version 410 core

layout(location = 0) in vec3 vec;

uniform mat4 mvp;

void main()
{
    // Make 4D vertex from 3D value.
    vec4 v = vec4(vec, 1.0);
    gl_Position = mvp * v;
}

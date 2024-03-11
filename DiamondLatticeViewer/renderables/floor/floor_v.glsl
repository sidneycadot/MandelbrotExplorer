
#version 410 core

layout(location = 0) in vec2 vec;

out vec2 fpos;

uniform mat4 projection_view_model_matrix;

void main()
{
    // Make 4D vertex from 2D value.
    fpos = vec;
    vec4 v = vec4(vec.x, 0.0, vec.y, 1.0);
    gl_Position = projection_view_model_matrix * v;
}


#version 410 core

layout(location = 0) out vec4 fragment_color;

void main()
{
    if (gl_FrontFacing)
    {
        fragment_color = vec4(1.0, 0.0, 1.0, 1.0);
    }
    else
    {
        fragment_color = vec4(1.0, 0.8, 1.0, 1.0);
    }
}

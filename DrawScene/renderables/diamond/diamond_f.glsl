
#version 410 core

layout(location = 0) out vec4 fragment_color;

in vec3 v_color;

void main()
{
    fragment_color = vec4(v_color, 1.0);

    if (false && !gl_FrontFacing)
    {
        fragment_color = vec4(1.0, 0.0, 0.0, 1.0);
    }
}

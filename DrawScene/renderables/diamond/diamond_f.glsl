
#version 410 core

layout(location = 0) out vec4 fragment_color;

in vec3 v_color;
in vec3 v_normal;

void main()
{
    fragment_color = vec4(0.5 + 0.5 * v_normal, 1.0);

    if (false && !gl_FrontFacing)
    {
        fragment_color = vec4(1.0, 0.0, 0.0, 1.0);
    }
}


#version 410 core

out vec4 fragment_color;

in vec2 tex_coord;

uniform sampler2D my_texture;

void main()
{
    fragment_color = texture(my_texture, tex_coord);

    if (!gl_FrontFacing)
    {
        fragment_color = vec4(1.0, 1.0 - fragment_color.y, 1.0 - fragment_color.z, 1.0);
    }
}

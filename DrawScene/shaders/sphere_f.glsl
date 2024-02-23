
#version 410 core

layout(location = 0) out vec4 fragment_color;

in vec2 tex_coord;

uniform sampler2D my_texture;

void main()
{
    fragment_color = texture(my_texture, tex_coord);
}

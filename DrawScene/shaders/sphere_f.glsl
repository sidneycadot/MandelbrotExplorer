
#version 410 core

out vec4 fragment_color;

in vec2 tex_coord;

uniform sampler2D my_texture;

void main()
{
    fragment_color = texture(my_texture, tex_coord);
    //if (tex_coord.x > 1)
    //    fragment_color = vec4(tex_coord.x, 1.0, 0.0, 1.0);
    //else
    //    fragment_color = vec4(tex_coord.x, 0.0, 0.0, 1.0);
}

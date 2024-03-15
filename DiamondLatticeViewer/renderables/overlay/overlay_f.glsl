
#version 410 core

out vec4 fragment_color;

in VS_OUT {
   vec2 overlay_texture_coordinate;
} fs_in;

uniform sampler2D overlay_texture;

void main()
{
    fragment_color = texture(overlay_texture, fs_in.overlay_texture_coordinate);
}

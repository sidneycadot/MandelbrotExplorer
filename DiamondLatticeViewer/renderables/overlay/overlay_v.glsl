
#version 410 core

layout(location = 0) in vec2 a_vertex;

out VS_OUT {
    vec2 overlay_texture_coordinate;
} vs_out;

uniform uvec2 frame_buffer_size;

uniform sampler2D overlay_texture;

void main()
{
    // Make 4D vertex from 3D value.
    vec4 v = vec4(a_vertex, -1, 1.0);

    uvec2 texture_size = textureSize(overlay_texture, 0);

    //   texture.x = 0.5 + 0.5 * vertex.x;
    //   texture.y = 0.5 - 0.5 * vertex.y;

    vs_out.overlay_texture_coordinate = vec2(0.5 + 0.5 * a_vertex.x, 0.5 - 0.5 * a_vertex.y);

    //   clipspace.x = vertex.x * texture_size.x / frame_buffer_size.x + offset_x
    //   -1 --> -1
    //   +1 --> -1 +
    //   clipspace.y = vertex.y * texture_size.y / frame_buffer_size.y


    float offset_x = 1 - float(texture_size.x) / frame_buffer_size.x;
    float offset_y = 1 - float(texture_size.y) / frame_buffer_size.y;

    gl_Position = vec4(
        a_vertex.x * texture_size.x / frame_buffer_size.x + offset_x,
        a_vertex.y * texture_size.y / frame_buffer_size.y - offset_y, 0.0, 1.0
    );
}

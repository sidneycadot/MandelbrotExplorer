
#version 410 core

layout(location = 0) in vec2 a_vertex;

out VS_OUT {
    vec2 overlay_texture_coordinate;
} vs_out;

void main()
{
    // Make 4D vertex from 3D value.
    vec4 v = vec4(a_vertex, -1, 1.0);

    vs_out.overlay_texture_coordinate = vec2(0.5 + 0.5 * a_vertex.x, 0.5 - 0.5 * a_vertex.y);

    gl_Position = v;
}

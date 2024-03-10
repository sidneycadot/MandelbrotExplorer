
#version 410 core

layout(location = 0) in vec3 a_vertex;

uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

uniform mat4 projection_view_model_matrix;
uniform mat4 view_model_matrix;

out VS_OUT {
    vec3 mv_coordinate;
} vs_out;

void main()
{
    // Make 4D vertex from 3D value.
    vec4 v = vec4(a_vertex, 1.0);

    vs_out.mv_coordinate = (view_model_matrix * v).xyz;

    gl_Position = projection_view_model_matrix * v;
}

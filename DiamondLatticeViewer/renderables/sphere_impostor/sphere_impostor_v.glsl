
#version 410 core

layout (location = 0) in vec3 a_vertex;

uniform mat4 transposed_inverse_view_model_matrix;
uniform mat4 projection_matrix;
uniform mat4 projection_view_model_matrix;
uniform mat4 view_model_matrix;

out VS_OUT {
    vec3 mv_impostor_surface;
    flat mat4 modelview_to_object_space_matrix;
    flat mat4 object_to_projection_space_matrix;
} vs_out;

void main()
{
    // Make 4D vertex from 3D value.
    vec4 v = vec4(a_vertex, 1.0);

    gl_Position = projection_view_model_matrix * v;
    vs_out.mv_impostor_surface = (view_model_matrix * v).xyz;

    vs_out.modelview_to_object_space_matrix = transpose(transposed_inverse_view_model_matrix);

    vs_out.object_to_projection_space_matrix = projection_matrix * inverse(vs_out.modelview_to_object_space_matrix);
}

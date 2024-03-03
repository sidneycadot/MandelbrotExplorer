
#version 410 core

layout (location = 0) in vec3 a_vertex;
layout (location = 1) in vec3 a_normal;
layout (location = 2) in ivec3 a_lattice_position;
layout (location = 3) in ivec3 a_lattice_delta;

uniform mat4 model_view_projection_matrix;
uniform mat4 model_view_matrix;
uniform mat4 transposed_inverse_model_view_matrix;

uniform uint cells_per_dimension;

out VS_OUT {
    vec3 mv_surface;
    vec3 mv_normal;
    vec3 color;
} vs_out;

vec3 vec4_to_vec3(vec4 v)
{
    return v.xyz / v.w;
}

const float UNIT_CELL_SIZE = 4.0;

bool valid_lattice_position(vec3 pos)
{
    return length(pos) <= 8.0;
}

void main()
{
    uint iz = gl_InstanceID;
    uint ix = iz % cells_per_dimension; iz /= cells_per_dimension;
    uint iy = iz % cells_per_dimension; iz /= cells_per_dimension;

    uvec3 unitcell_index_vector = uvec3(ix, iy, iz);

    vec3 unitcell_displacement_vector = UNIT_CELL_SIZE * (unitcell_index_vector - 0.5 * cells_per_dimension);

    // Do we want to render this triangle?

    vec3 lattice_position = unitcell_displacement_vector + a_lattice_position;

    vec3 vertex_position = unitcell_displacement_vector + a_vertex;

    bool render_flag = true;

    if (!valid_lattice_position(lattice_position))
    {
        render_flag = false;
    }
    else
    {
        lattice_position += a_lattice_delta;
        if (!valid_lattice_position(lattice_position))
        {
            render_flag = false;
        }
    }

    if (!render_flag)
    {
        // Emit a zero triangle, which will be discarded.
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
    }
    else
    {
        gl_Position = model_view_projection_matrix * vec4(vertex_position, 1.0);
        vs_out.mv_surface = vec4_to_vec3(model_view_matrix * vec4(vertex_position, 1.0));
        vs_out.mv_normal = normalize((transposed_inverse_model_view_matrix * vec4(a_normal, 0.0)).xyz);

        if (a_lattice_delta.x == 0)
        {
            // Carbon sphere.
            vs_out.color = 0.2 + 0.8 * a_lattice_position / 3;
        }
        else
        {
            // Carbon-carbon joint cylinder.
            vs_out.color = vec3(1.0, 1.0, 1.0);
        }
    }
}


#version 410 core

layout (location = 0) in vec3 a_vertex;
layout (location = 1) in vec3 a_lattice_position;
layout (location = 2) in vec3 a_lattice_delta;
layout (location = 3) in vec4 a_inverse_placement_matrix_row1;
layout (location = 4) in vec4 a_inverse_placement_matrix_row2;
layout (location = 5) in vec4 a_inverse_placement_matrix_row3;

uniform mat4 projection_view_model_matrix;
uniform mat4 view_model_matrix;
uniform mat4 transposed_inverse_view_model_matrix;
uniform mat4 projection_matrix;

uniform uint cut_mode;
uniform uint unit_cells_per_dimension;
uniform float diamond_lattice_side_length;
uniform uint color_mode;

out VS_OUT {
    vec3 mv_impostor_surface;
    vec3 color;
    flat mat4 modelview_to_object_space_matrix;
    flat mat4 object_to_projection_space_matrix;
    flat uint object_type; // 0 == sphere, 1 == cylinder.
} vs_out;

const float UNIT_CELL_SIZE = 4.0;

const vec3 cut100_normal = normalize(vec3(1, 0, 0));
const vec3 cut110_normal = normalize(vec3(1, 1, 0));
const vec3 cut111_normal = normalize(vec3(1, 1, 1));

const float positive_infinity = +1e30; // Certainly outside of crystal.
const float negative_infinity = -1e30; // Certainly inside of crystal.

const float cut_surface_threshold = 1e-3;

float crystal_lattice_surface_cut_distance(vec3 pos)
{
    // Positive : outside crystal.
    // Negative : inside crystal.

    bool candidate = max(abs(pos.x), max(abs(pos.y), abs(pos.z))) <= 0.5 * diamond_lattice_side_length;
    //bool candidate = length(pos) <= 0.5 * diamond_lattice_side_length + 0.1;
    if (!candidate)
    {
        return positive_infinity; // Outside of crystal.
    }

    switch (cut_mode)
    {
        case 1: return dot(cut100_normal, pos);
        case 2: return dot(cut110_normal, pos);
        case 3: return dot(cut111_normal, pos);
    }

    return negative_infinity; // Inside of crystal.
}

void main()
{
    uint iz = gl_InstanceID;
    uint ix = iz % unit_cells_per_dimension; iz /= unit_cells_per_dimension;
    uint iy = iz % unit_cells_per_dimension; iz /= unit_cells_per_dimension;

    uvec3 unit_cell_index_vector = uvec3(ix, iy, iz);

    // 1 --> 0
    // 3 --> -1
    // 5 --> -2
    vec3 unit_cell_displacement_vector = UNIT_CELL_SIZE * (unit_cell_index_vector - 0.5 * (unit_cells_per_dimension - 1));

    // Do we want to render this triangle?

    vec3 lattice_position = unit_cell_displacement_vector + a_lattice_position;

    float carbon_cut_distance = crystal_lattice_surface_cut_distance(lattice_position);

    bool render_flag = true;
    if (carbon_cut_distance > cut_surface_threshold)
    {
        render_flag = false;
    }
    else
    {
        if (crystal_lattice_surface_cut_distance(lattice_position + a_lattice_delta) > cut_surface_threshold)
        {
            render_flag = false;
        }
    }

    if (!render_flag)
    {
        // Emit a zero triangle which will be discarded.
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
    }
    else
    {
        vec3 vertex_position = unit_cell_displacement_vector + a_vertex;

        gl_Position = projection_view_model_matrix * vec4(vertex_position, 1.0);
        vs_out.mv_impostor_surface = (view_model_matrix * vec4(vertex_position, 1.0)).xyz;

        vs_out.object_type = (a_lattice_delta.x == 0) ? 0 : 1;

        mat4 inverse_displacement_matrix = mat4(
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            -unit_cell_displacement_vector.x, -unit_cell_displacement_vector.y, -unit_cell_displacement_vector.z, 1
        );

        mat4 inverse_placement_matrix = mat4x4(
            a_inverse_placement_matrix_row1[0], a_inverse_placement_matrix_row2[0], a_inverse_placement_matrix_row3[0], 0,
            a_inverse_placement_matrix_row1[1], a_inverse_placement_matrix_row2[1], a_inverse_placement_matrix_row3[1], 0,
            a_inverse_placement_matrix_row1[2], a_inverse_placement_matrix_row2[2], a_inverse_placement_matrix_row3[2], 0,
            a_inverse_placement_matrix_row1[3], a_inverse_placement_matrix_row2[3], a_inverse_placement_matrix_row3[3], 1
        );

        vs_out.modelview_to_object_space_matrix = inverse_placement_matrix * inverse_displacement_matrix * transpose(transposed_inverse_view_model_matrix);

        vs_out.object_to_projection_space_matrix = projection_matrix * inverse(vs_out.modelview_to_object_space_matrix);

        // Determine the color of the triangle.

        switch (color_mode)
        {
            case 0: // Color white (possible colored plane for cuts).
            {
                if (a_lattice_delta.x == 0)
                {
                    // Carbon atom (sphere).
                    switch (cut_mode)
                    {
                        case 1: vs_out.color = (carbon_cut_distance > -2.3) ? vec3(1.0, 0.0, 0.0) : vec3(1.0, 1.0, 1.0); break;
                        case 2: vs_out.color = (carbon_cut_distance > -2.3) ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 1.0, 1.0); break;
                        case 3: vs_out.color = (carbon_cut_distance > -2.3) ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 1.0, 1.0); break;
                        default : vs_out.color = vec3(1.0, 1.0, 1.0); break;
                    }
                }
                else
                {
                    // Carbon-carbon bond (cylinder).
                    vs_out.color = vec3(1.0, 1.0, 1.0);
                }
                break;
            }
            case 1: // Color according to position in the grid
            {
                if (a_lattice_delta.x == 0)
                {
                    // Carbon atom (sphere).
                    vs_out.color = 0.55 + 0.45 * a_lattice_position / 1.5;
                }
                else
                {
                    // Carbon-carbon bond (cylinder).
                    vs_out.color =  vec3(1.0, 1.0, 1.0);
                }
                break;
            }
            case 2: // Color according to position in the grid
            {
                if (a_lattice_delta.x == 0)
                {
                    // Carbon atom (sphere).
                    if (mod(a_lattice_position.x + a_lattice_position.y + a_lattice_position.z +1.5, 4) == 0)
                    {
                        vs_out.color = vec3(1.0, 0.0, 0.0);
                    }
                    else
                    {
                        vs_out.color = vec3(1.0, 1.0, 0.0);
                    }
                }
                else
                {
                    // Carbon-carbon bond (cylinder).
                    vs_out.color = vec3(1.0, 1.0, 1.0);
                }
                break;
            }
        }
    }
}

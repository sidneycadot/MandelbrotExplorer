
#version 410 core

layout (location = 0) in vec3 a_vertex;
layout (location = 1) in vec3 a_normal;
layout (location = 2) in ivec3 a_lattice_position;
layout (location = 3) in ivec3 a_lattice_delta;

uniform mat4 model_view_projection_matrix;
uniform mat4 model_view_matrix;
uniform mat4 transposed_inverse_model_view_matrix;

uniform uint cut;
uniform uint unit_cells_per_dimension;
uniform float crystal_side_length;
uniform uint color_mode;

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

int crystal_lattice_position_type(vec3 pos)
{
    // Return +1 : outside crystal.
    // Return  0 : inside crystal, on cut surface.
    // Return -1 : inside crystal, below cut surface.

    bool candidate = max(abs(pos.x), max(abs(pos.y), abs(pos.z))) <= 0.5 * crystal_side_length;
    if (!candidate)
    {
        return +1;
    }

    switch (cut)
    {
        case 0: return -1;
        case 1: return int(sign(pos.x));
        case 2: return int(sign(pos.x + pos.y));
        case 3: return int(sign(pos.x + pos.y + pos.z + 1));
    }
}

void main()
{
    uint iz = gl_InstanceID;
    uint ix = iz % unit_cells_per_dimension; iz /= unit_cells_per_dimension;
    uint iy = iz % unit_cells_per_dimension; iz /= unit_cells_per_dimension;

    uvec3 unit_cell_index_vector = uvec3(ix, iy, iz);

    vec3 unit_cell_displacement_vector = UNIT_CELL_SIZE * (unit_cell_index_vector - 0.5 * unit_cells_per_dimension);

    // Do we want to render this triangle?

    vec3 lattice_position = unit_cell_displacement_vector + a_lattice_position;

    vec3 vertex_position = unit_cell_displacement_vector + a_vertex;

    bool render_flag = true;

    int carbon_position_type = crystal_lattice_position_type(lattice_position);
    if (carbon_position_type > 0)
    {
        render_flag = false;
    }
    else
    {
        lattice_position += a_lattice_delta;
        if (crystal_lattice_position_type(lattice_position) > 0)
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

        switch(color_mode)
        {
            case 0:
            {
                if (a_lattice_delta.x == 0)
                {
                    // Carbon atom (sphere).
                    vs_out.color = 0.2 + 0.9 * a_lattice_position / 3;
                }
                else
                {
                    // Carbon-carbon bond (cylinder).
                    vs_out.color = vec3(1.0, 1.0, 1.0);
                }
                break;
            }
            case 1:
            {
                if (a_lattice_delta.x == 0)
                {
                    // Carbon atom (sphere).
                    if (carbon_position_type < 0)
                    {
                        vs_out.color = vec3(1.0, 1.0, 1.0);
                    }
                    else
                    {
                        vs_out.color = vec3(1.0, 0.0, 0.0);
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

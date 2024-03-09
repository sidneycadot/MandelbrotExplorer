
#version 410 core

uniform mat4 transposed_inverse_view_matrix;
uniform mat4 inverse_view_model_matrix;
uniform mat4 projection_matrix;

layout(location = 0) out vec4 fragment_color;

in VS_OUT {
    vec3 mv_surface;
    vec3 color;
    flat ivec3 a_lattice_position;
    flat ivec3 a_lattice_delta;
    flat mat4x3 a_inverse_placement_matrix;
} fs_in;

// Intensities.
const float ia = 0.2;
const float id1 = 0.6;
const float is1 = 0.5;
//const float id2 = 0.5;
//const float is2 = 0.5;

const float phong_alpha = 20;

const float INVALID = -1.0;

float intersect_unit_sphere(vec3 origin, vec3 direction)
{
    // See: https://en.wikipedia.org/wiki/Line–sphere_intersection
    //
    // Find smallest real alpha such that: origin + alpha * direction is on the unit sphere.
    //
    float oo = dot(origin, origin);
    float uo = dot(direction, origin);
    float uu = dot(direction, direction);
    float discriminant = uo*uo - uu * (oo - 1);

    // Early abort if a solution does not exist.
    // This check can be omitted, but it is adventageous to keep it for improved performance.
    if (discriminant < 0)
    {
        return INVALID;
    }
    return (-uo - sqrt(discriminant)) / uu;
}

float intersect_unit_cylinder(vec2 origin, vec2 direction)
{
    // See: https://en.wikipedia.org/wiki/Line–sphere_intersection
    //
    // Find smallest real alpha such that: origin + alpha * direction is on the unit cylinder.
    // The unit-cylinder stretched for -inf to +inf in the Z direction.
    //
    float oo = dot(origin, origin);
    float uo = dot(direction, origin);
    float uu = dot(direction, direction);
    float discriminant = uo*uo - uu * (oo - 1);

    // Early abort if a solution does not exist.
    // This check can be omitted, but it is adventageous to keep it for improved performance.
    if (discriminant < 0)
    {
        return INVALID;
    }
    return (-uo - sqrt(discriminant)) / uu;
}

void main()
{
    if (fs_in.a_lattice_delta.x == 0)
    {
        // The triangle is part of a sphere impostor hull.

        mat4 inverse_placement_matrix = mat4(
            fs_in.a_inverse_placement_matrix[0][0], fs_in.a_inverse_placement_matrix[0][1], fs_in.a_inverse_placement_matrix[0][2], 0,
            fs_in.a_inverse_placement_matrix[1][0], fs_in.a_inverse_placement_matrix[1][1], fs_in.a_inverse_placement_matrix[1][2], 0,
            fs_in.a_inverse_placement_matrix[2][0], fs_in.a_inverse_placement_matrix[2][1], fs_in.a_inverse_placement_matrix[2][2], 0,
            fs_in.a_inverse_placement_matrix[3][0], fs_in.a_inverse_placement_matrix[3][1], fs_in.a_inverse_placement_matrix[3][2], 1
        );

        mat4 to_obj_space = inverse_placement_matrix * inverse_view_model_matrix;

        vec3 h = (to_obj_space * vec4(fs_in.mv_surface, 1)).xyz;
        vec3 e = (to_obj_space * vec4(0, 0, 0, 1)).xyz;

        vec3 eh = h - e; // eye-to-hitpoint vector.

        float alpha = intersect_unit_sphere(e, eh);

        if (alpha == INVALID)
        {
            discard;
        }

        // This is the point where the ray and the unit sphere intersect in the "unit sphere" coordinate system.
        // It is normalized since it is on the unit sphere.
        vec3 sphere_hit = e + alpha * eh;

        // Fix depth.

        vec4 projection = projection_matrix * inverse(to_obj_space) * vec4(sphere_hit, 1);

        gl_FragDepth = 0.5 + 0.5 *  (projection.z / projection.w);

        // Render sphere from sphere envelope.
        vec3 k_material = fs_in.color;

        // NOTE: We do our geometric calculations in the "MV" coordinate system.

        vec3 mv_eye = vec3(0, 0, 0);
        vec3 mv_surface = fs_in.mv_surface;
        vec3 mv_surface_normal = normalize((transpose(to_obj_space) * vec4(sphere_hit, 1)).xyz);
        vec3 mv_viewer_direction = normalize(mv_eye-mv_surface);

        vec3 m_lightsource1_direction = normalize(vec3(+1, 1, 1));
        vec3 mv_lightsource1_direction = normalize((transposed_inverse_view_matrix * vec4(m_lightsource1_direction, 0)).xyz);
        vec3 mv_lightsource1_reflection_direction = 2 * dot(mv_lightsource1_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource1_direction;

        //vec3 m_lightsource2_direction = normalize(vec3(-1, 1, 1));
        //vec3 mv_lightsource2_direction = normalize((transposed_inverse_view_matrix * vec4(m_lightsource2_direction, 0)).xyz);
        //vec3 mv_lightsource2_reflection_direction = 2 * dot(mv_lightsource2_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource2_direction;

        float contrib_d1 = max(0.0, dot(mv_lightsource1_direction, mv_surface_normal));
        float contrib_s1 = pow(max(0.0, dot(mv_lightsource1_reflection_direction, mv_viewer_direction)), phong_alpha);

        //float contrib_d2 = max(0.0, dot(mv_lightsource2_direction, mv_surface_normal));
        //float contrib_s2 = pow(max(0.0, dot(mv_lightsource2_reflection_direction, mv_viewer_direction)), alpha);

        vec3 phong_color = k_material * (ia + id1 * contrib_d1 + is1 * contrib_s1);
        //vec3 phong_color = k_material * (ia + id1 * contrib_d1 + is1 * contrib_s1 + id2 * contrib_d2 + is2 * contrib_s2);

        fragment_color = vec4(phong_color, 1.0);
    }
    else
    {
        // The triangle is part of a cylinder impostor hull.

        mat4 inverse_placement_matrix = mat4(
            fs_in.a_inverse_placement_matrix[0][0], fs_in.a_inverse_placement_matrix[0][1], fs_in.a_inverse_placement_matrix[0][2], 0,
            fs_in.a_inverse_placement_matrix[1][0], fs_in.a_inverse_placement_matrix[1][1], fs_in.a_inverse_placement_matrix[1][2], 0,
            fs_in.a_inverse_placement_matrix[2][0], fs_in.a_inverse_placement_matrix[2][1], fs_in.a_inverse_placement_matrix[2][2], 0,
            fs_in.a_inverse_placement_matrix[3][0], fs_in.a_inverse_placement_matrix[3][1], fs_in.a_inverse_placement_matrix[3][2], 1
        );

        mat4 to_obj_space = inverse_placement_matrix * inverse_view_model_matrix;

        vec3 h = (to_obj_space * vec4(fs_in.mv_surface, 1)).xyz;
        vec3 e = (to_obj_space * vec4(0, 0, 0, 1)).xyz;

        vec3 eh = h - e; // eye-to-hitpoint vector.

        float alpha = intersect_unit_cylinder(e.xy, eh.xy);

        if (alpha == INVALID)
        {
            //fragment_color = vec4(1, 0, 0, 1);
            //return;
            discard;
        }

        // This is the point where the ray and the unit cylinder intersect in the "unit cylinder" coordinate system.
        // Its xy coordinates are normalized since they are a point on the unit cylinder.
        vec3 cylinder_hit = e + alpha * eh;

        if (abs(cylinder_hit.z) > 0.5)
        {
            // The cylinder is hit, but outside its z range [-0.5 .. +0.5].
            //fragment_color = vec4(0.0, 1.0, 1.0, 1.0);
            //return;
            discard;
        }

        // Fix depth.

        vec4 projection = projection_matrix * inverse(to_obj_space) * vec4(cylinder_hit, 1);

        gl_FragDepth = 0.5 + 0.5 *  (projection.z / projection.w);

        // Render sphere from sphere envelope.
        vec3 k_material = fs_in.color;

        // NOTE: We do our geometric calculations in the "MV" coordinate system.

        vec3 mv_eye = vec3(0, 0, 0);
        vec3 mv_surface = fs_in.mv_surface;
        vec3 mv_surface_normal = normalize((transpose(to_obj_space) * vec4(cylinder_hit, 1)).xyz);
        vec3 mv_viewer_direction = normalize(mv_eye-mv_surface);

        vec3 m_lightsource1_direction = normalize(vec3(+1, 1, 1));
        vec3 mv_lightsource1_direction = normalize((transposed_inverse_view_matrix * vec4(m_lightsource1_direction, 0)).xyz);
        vec3 mv_lightsource1_reflection_direction = 2 * dot(mv_lightsource1_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource1_direction;

        //vec3 m_lightsource2_direction = normalize(vec3(-1, 1, 1));
        //vec3 mv_lightsource2_direction = normalize((transposed_inverse_view_matrix * vec4(m_lightsource2_direction, 0)).xyz);
        //vec3 mv_lightsource2_reflection_direction = 2 * dot(mv_lightsource2_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource2_direction;

        float contrib_d1 = max(0.0, dot(mv_lightsource1_direction, mv_surface_normal));
        float contrib_s1 = pow(max(0.0, dot(mv_lightsource1_reflection_direction, mv_viewer_direction)), phong_alpha);

        //float contrib_d2 = max(0.0, dot(mv_lightsource2_direction, mv_surface_normal));
        //float contrib_s2 = pow(max(0.0, dot(mv_lightsource2_reflection_direction, mv_viewer_direction)), alpha);

        vec3 phong_color = k_material * (ia + id1 * contrib_d1 + is1 * contrib_s1);
        //vec3 phong_color = k_material * (ia + id1 * contrib_d1 + is1 * contrib_s1 + id2 * contrib_d2 + is2 * contrib_s2);

        fragment_color = vec4(phong_color, 1.0);
    }
}

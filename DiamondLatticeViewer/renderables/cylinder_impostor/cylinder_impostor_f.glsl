
#version 410 core

out vec4 fragment_color;

in VS_OUT {
    vec3 m_coordinate;
    vec3 mv_coordinate;
} fs_in;

uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

uniform mat4 view_model_matrix;
uniform mat4 transposed_inverse_view_model_matrix;
uniform mat4 transposed_inverse_view_matrix;

uniform sampler2D my_texture;

const float PI = 4 * atan(1);

// Note: we don't use NaN as an invalid value because it somehow doesn't work correctly
//   on a relatively modern nVidia card.
const float INVALID = -1;

const float ia = 0.2;
const float id1 = 0.6;
const float is1 = 1.02;

const float phong_alpha = 20.0;

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
    // We receive model and modelview coordinates from the vertex shader.

    // Get the eye coordinate in "original object vertex" coordinates:

    mat4 inverse_model_view_matrix = inverse(view_matrix * model_matrix);

    // "e" is the eye position in the "unit cylinder" coordinate system.
    vec3 e = (inverse_model_view_matrix * vec4(0, 0, 0, 1)).xyz;

    // "h" is the impostor hitpoint position in the "unit cylinder" coordinate system.
    vec3 h = (inverse_model_view_matrix * vec4(fs_in.mv_coordinate, 1)).xyz;

    // Solve:
    //   ray[alpha] := e + alpha * (h - e)
    // Find the smallest real value alpha such that ray[alpha]) intersects the unit cylinder.

    vec3 eh = h - e;

    float alpha = intersect_unit_cylinder(e.xy, eh.xy);

    if (alpha == INVALID)
    {
        //fragment_color = vec4(1.0, 1.0, 0.0, 1.0);
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

    // Find texture coordinates.

    float u = 0.5 + 0.5 * atan(cylinder_hit.x, cylinder_hit.y) / PI;
    float v = 0.5 + cylinder_hit.z;

    vec3 k_material = texture(my_texture, vec2(u, v)).xyz;

    // Fix depth.

    vec4 proj = projection_matrix * view_matrix * model_matrix * vec4(cylinder_hit, 1);
    float depth = (proj.z / proj.w);

    gl_FragDepth = 0.5 + 0.5 * depth;

    // Do phong shading.

    vec3 mv_surface = (view_model_matrix * vec4(cylinder_hit, 1)).xyz;
    vec3 mv_surface_normal = normalize((transposed_inverse_view_model_matrix * vec4(cylinder_hit, 1)).xyz);
    vec3 mv_viewer_direction = normalize(-mv_surface);

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


#version 410 core

out vec4 fragment_color;

in VS_OUT {
    vec3 mv_coordinate;
} fs_in;

uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

uniform mat4 inverse_view_model_matrix;
uniform mat4 view_model_matrix;
uniform mat4 projection_view_model_matrix;
uniform mat4 transposed_inverse_view_matrix;
uniform mat4 transposed_inverse_view_model_matrix;
uniform mat4 transposed_inverse_projection_view_model_matrix;

uniform sampler2D my_texture;
const float INVALID = 1.0 / 0.0;

const float PI = 4 * atan(1);

const float ia = 0.2;
const float id1 = 0.6;
const float is1 = 1.02;

const float phong_alpha = 20.0;

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

void main()
{
    // We receive model and modelview coordinates from the vertex shader.

    // "e" is the eye position in the "unit sphere" coordinate system.
    vec3 e = (inverse_view_model_matrix * vec4(0, 0, 0, 1)).xyz;

    // "h" is the impostor hitpoint position in the "unit sphere" coordinate system.
    vec3 h = (inverse_view_model_matrix * vec4(fs_in.mv_coordinate, 1)).xyz;

    // Solve:    ray[alpha] := e + alpha * (h - e)
    // Find the smallest real value alpha such that ray[alpha]) intersects the unit sphere.

    vec3 eh = h - e; // eye-to-hitpoint vector.

    float alpha = intersect_unit_sphere(e, eh);

    if (alpha == INVALID)
    {
        discard;
    }

    // This is the point where the ray and the unit sphere intersect in the "unit sphere" coordinate system.
    // It is normalized since it is on the unit sphere.
    vec3 sphere_hit = e + alpha * eh;

    // Find texture coordinates.

    float u = 0.5 + 0.5 * atan(sphere_hit.x, sphere_hit.z) / PI;
    float v = 0.5 - 0.5 * sphere_hit.y;

    vec3 k_material = texture(my_texture, vec2(u, v)).xyz;

    // Fix depth.

    vec4 projection = projection_view_model_matrix * vec4(sphere_hit, 1);

    gl_FragDepth = 0.5 + 0.5 *  (projection.z / projection.w);

    // Do phong shading.

    vec3 mv_surface = (view_model_matrix * vec4(sphere_hit, 1)).xyz;
    vec3 mv_surface_normal = normalize((transposed_inverse_view_model_matrix * vec4(sphere_hit, 1)).xyz);
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

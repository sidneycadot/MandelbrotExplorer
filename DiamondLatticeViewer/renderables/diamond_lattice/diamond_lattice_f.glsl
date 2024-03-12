
#version 410 core

uniform mat4 transposed_inverse_view_matrix;
uniform mat4 inverse_view_model_matrix;
uniform uint impostor_mode;

in VS_OUT {
    vec3 mv_surface;
    vec3 color;
    flat mat4x4 modelview_to_object_space_matrix;
    flat mat4x4 object_to_projection_space_matrix;
    flat int object_type; // 0 == sphere, 1 == cylinder.
} fs_in;

layout(location = 0) out vec4 fragment_color;

// Phong shading intensities.
const float ia  = 0.2; // Ambient intensity.
const float id1 = 0.6; // Diffuse intensity of the first light source.
const float is1 = 0.5; // Specular intensity of the first light source.

const float phong_alpha = 20; // Alpha value for specular reflection.

const vec3 m_lightsource1_direction = normalize(vec3(+1, 1, 1));

uniform sampler2D my_texture;

// Note: we don't use NaN as an invalid value because it somehow doesn't work correctly
//   on a relatively modern nVidia card.
const float INVALID = -1.0;

const float PI = 4 * atan(1);

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
    vec3 object_impostor_hit = (fs_in.modelview_to_object_space_matrix * vec4(fs_in.mv_surface, 1)).xyz;
    vec3 object_eye = (fs_in.modelview_to_object_space_matrix * vec4(0, 0, 0, 1)).xyz;

    vec3 object_eye_to_impostor_hit_vector = object_impostor_hit - object_eye; // eye-to-hitpoint vector.

    float alpha = (fs_in.object_type == 0) ? intersect_unit_sphere(object_eye, object_eye_to_impostor_hit_vector) : intersect_unit_cylinder(object_eye.xy, object_eye_to_impostor_hit_vector.xy);

    if (alpha < 0)
    {
        if (impostor_mode == 0)
        {
            discard;
        }
        else
        {
            fragment_color = vec4(1, 1, 0, 1);
            return;
        }
    }

    // This is the point where the ray and the object intersect in the "object" coordinate system.
    // It is normalized since it is on the unit sphere or unit cylinder.

    vec3 object_hit = object_eye + alpha * object_eye_to_impostor_hit_vector;

    if (fs_in.object_type == 1 && abs(object_hit.z) > 0.5)
    {
        if (impostor_mode == 0)
        {
            discard;
        }
        else
        {
            fragment_color = vec4(0, 1, 1, 1);
            return;
        }
    }

    // Fix fragment depth. We replace the depth of the hull with the depth of the actual hitpoint
    // of the enclosed object.

    vec4 projection = fs_in.object_to_projection_space_matrix * vec4(object_hit, 1);

    gl_FragDepth = 0.5 + 0.5 *  (projection.z / projection.w);

    vec3 object_normal = (fs_in.object_type == 0) ? object_hit : vec3(object_hit.xy, 0);

    // Determine fragment color using Phong shading.

    vec3 k_material = fs_in.color;

    // NOTE: We do our geometric calculations in the "MV" coordinate system.

    vec3 mv_eye = vec3(0, 0, 0);
    vec3 mv_surface = fs_in.mv_surface;
    vec3 mv_surface_normal = normalize((transpose(fs_in.modelview_to_object_space_matrix) * vec4(object_normal, 0)).xyz);
    vec3 mv_viewer_direction = normalize(mv_eye - mv_surface);

    vec3 mv_lightsource1_direction = normalize((transposed_inverse_view_matrix * vec4(m_lightsource1_direction, 0)).xyz);
    vec3 mv_lightsource1_reflection_direction = 2 * dot(mv_lightsource1_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource1_direction;

    float contrib_d1 = max(0.0, dot(mv_lightsource1_direction, mv_surface_normal));
    float contrib_s1 = pow(max(0.0, dot(mv_lightsource1_reflection_direction, mv_viewer_direction)), phong_alpha);

    //if (fs_in.object_type == 2) // disabled.
    //{
    //    float u = 0.5 + 0.5 * atan(object_hit.x, object_hit.z) / PI;
    //    float v = 0.5 - 0.5 * object_hit.y;
    //
    //    k_material *= texture(my_texture, vec2(u, v)).xyz;
    //}

    vec3 phong_color = k_material * (ia + id1 * contrib_d1 + is1 * contrib_s1);

    fragment_color = vec4(phong_color, 1.0);
}

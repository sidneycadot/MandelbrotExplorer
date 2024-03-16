
#version 410 core

#ifdef GL_ARB_conservative_depth
#extension GL_ARB_conservative_depth : enable
#endif

// Constants.

const float PI = 4 * atan(1);

// Uniform variables.

uniform mat4 transposed_inverse_view_matrix;
uniform uint impostor_mode;
uniform sampler2D my_texture;

// Input variables provided by the vertex shader.

in VS_OUT {
    vec3 mv_impostor_surface;
    flat mat4 modelview_to_object_space_matrix;
    flat mat4 object_to_projection_space_matrix;
} fs_in;

// Fragment shader output variables.

layout (location = 0) out vec4 fragment_color;

#ifdef GL_ARB_conservative_depth
// We guarantee that gl_FragDepth will be greater than or equal to gl_FragCoord.z.
// This allows safe depth-tests before the fragment shader is run, gaining performance.
layout (depth_greater) out float gl_FragDepth;
#endif

// Phong shading parameters.

const float ia = 0.2;
const float id1 = 0.6;
const float is1 = 1.02;

const float phong_alpha = 20.0;

const vec3 m_lightsource1_direction = normalize(vec3(+1, 1, 1));

// Intersection function: ray/cylinder.

// Note: we don't use NaN as an invalid value because it somehow doesn't work correctly
//   on a relatively modern nVidia card.
const float INVALID = -1.0;

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

    if (discriminant < 0)
    {
        return INVALID;
    }

    return (-uo - sqrt(discriminant)) / uu;
}

void main()
{
    vec3 object_impostor_hit = (fs_in.modelview_to_object_space_matrix * vec4(fs_in.mv_impostor_surface, 1)).xyz;
    vec3 object_eye = (fs_in.modelview_to_object_space_matrix * vec4(0, 0, 0, 1)).xyz;

    vec3 object_eye_to_impostor_hit_vector = object_impostor_hit - object_eye; // eye-to-hitpoint vector.

    float alpha = intersect_unit_cylinder(object_eye.xy, object_eye_to_impostor_hit_vector.xy);

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

    // This is the point where the ray and the unit cylinder intersect in the "unit cylinder" coordinate system.
    // Its xy coordinates are normalized since they are a point on the unit cylinder.
    vec3 object_hit = object_eye + alpha * object_eye_to_impostor_hit_vector;

    if (abs(object_hit.z) > 0.5)
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

    float new_frag_depth =  0.5 + 0.5 *  (projection.z / projection.w);

    if (!(new_frag_depth >= gl_FragCoord.z))
    {
        // We have promised that gl_FragDepth we'll write will be greater than or equal to the depth value
        // of the fragment currently being rasterized; see the gl_FragDepth declaration near the top of
        // the file.
        //
        // Since our impostor hull triangles completely envelop the contained objects (sphere or cylinder),
        // this shouldn't mathematically happen. Still, it just did!
        //
        // This appears to be caused by numerical imprecision (on an nVidia desktop system at least).
        //
        // We handle this by simply discarding the fragment, if the depth we're about to write doesn't
        // comply with "the depth may not decrease" constraint, thus keeping our promise.

        discard;
    }

    gl_FragDepth = new_frag_depth;

    // Find texture color.

    float u = 0.5 + 0.5 * atan(object_hit.x, object_hit.y) / PI;
    float v = 0.5 + object_hit.z;

    vec3 k_material = texture(my_texture, vec2(u, v)).xyz;

    // Determine fragment color using Phong shading.

    vec3 object_normal = object_hit; // For a unit sphere, the normal vector is the object hitpoint.

    vec3 mv_eye = vec3(0, 0, 0);
    vec3 mv_impostor_surface = fs_in.mv_impostor_surface;
    vec3 mv_surface_normal = normalize((transpose(fs_in.modelview_to_object_space_matrix) * vec4(object_normal, 0)).xyz);
    vec3 mv_viewer_direction = normalize(mv_eye - mv_impostor_surface);

    vec3 mv_lightsource1_direction = normalize((transposed_inverse_view_matrix * vec4(m_lightsource1_direction, 0)).xyz);
    vec3 mv_lightsource1_reflection_direction = 2 * dot(mv_lightsource1_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource1_direction;

    float contrib_d1 = max(0.0, dot(mv_lightsource1_direction, mv_surface_normal));
    float contrib_s1 = pow(max(0.0, dot(mv_lightsource1_reflection_direction, mv_viewer_direction)), phong_alpha);

    vec3 phong_color = k_material * (ia + id1 * contrib_d1 + is1 * contrib_s1);

    fragment_color = vec4(phong_color, 1.0);
}

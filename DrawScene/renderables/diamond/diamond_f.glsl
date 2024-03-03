
#version 410 core

uniform mat4 m_projection;
uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_transpose_inverse_view;

layout(location = 0) out vec4 fragment_color;

in VS_OUT {
    vec3 mv_surface;
    vec3 mv_normal;
    flat ivec3 a_lattice_position;
    flat ivec3 a_lattice_delta;
    vec3 color;
} fs_in;

// Project vector a onto vector b.
vec3 proj(vec3 avec, vec3 bvec)
{
    return dot(avec, bvec) / dot(bvec, bvec) * bvec;
}

vec3 reflect(vec3 L, vec3 N)
{
    return 2 * proj(L, N) - L;
}

// Intensities.
const vec3 ia = vec3(0.2, 0.2, 0.2);
const vec3 id = vec3(1.0, 1.0, 1.0);
const vec3 is = vec3(1.0, 1.0, 1.0);

const float alpha = 100.0;

void main()
{
    vec3 k_material = fs_in.color;

    // NOTE: We make all our vectors in the "MV" coordinate system.

    vec3 mv_eye = vec3(0, 0, 0);
    vec3 mv_surface = fs_in.mv_surface;
    vec3 mv_surface_normal = normalize(fs_in.mv_normal);

    vec3 m_lightsource_direction = vec3(0,1,0);
    vec3 mv_lightsource_direction = normalize((m_transpose_inverse_view * vec4(m_lightsource_direction, 0)).xyz);
    vec3 mv_lightsource_reflection_direction = 2 * dot(mv_lightsource_direction, mv_surface_normal) * mv_surface_normal - mv_lightsource_direction;
    vec3 mv_viewer_direction = normalize(mv_eye - mv_surface);

    float contrib_d = max(0, dot(mv_lightsource_direction, mv_surface_normal));
    float contrib_s = max(0, pow(dot(mv_lightsource_reflection_direction, mv_viewer_direction), alpha));

    vec3 intensity = k_material * (ia + id * contrib_d + is * contrib_s);

    fragment_color = vec4(intensity, 1.0);

    if (false && !gl_FrontFacing)
    {
        fragment_color = vec4(1.0, 0.0, 0.0, 1.0);
    }
}


#version 410 core

layout(location = 0) out vec4 fragment_color;

in VS_OUT {
    vec3 mv_surface;
    vec3 mv_normal;
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

void main()
{
    vec3 mv_surface = fs_in.mv_surface;
    vec3 surface_normal = normalize(fs_in.mv_normal);
    vec3 mv_lamp = normalize(vec3(0, 0, 1000));
    vec3 mv_eye = vec3(0, 0, 0);

    vec3 lamp_specular_reflection_vector = reflect(mv_lamp - mv_surface, surface_normal);

    float angle = dot(normalize(surface_normal), normalize(mv_eye - mv_surface));
    //fragment_color = vec4(0.5 + 0.5 * normalize(fs_in.mv_normal), 1.0);
    fragment_color = vec4(angle, angle, angle, 1.0);

    if (false && !gl_FrontFacing)
    {
        fragment_color = vec4(1.0, 0.0, 0.0, 1.0);
    }
}

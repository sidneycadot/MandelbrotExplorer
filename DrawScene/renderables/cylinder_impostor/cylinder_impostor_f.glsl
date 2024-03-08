
#version 410 core

out vec4 fragment_color;

in VS_OUT {
    vec3 m_coordinate;
    vec3 mv_coordinate;
} fs_in;

uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

uniform sampler2D my_texture;

const float PI = 4 * atan(1);
const float NaN = 0.0 / 0.0;


float intersect_unit_cylinder(vec2 origin, vec2 direction)
{
    // See: https://en.wikipedia.org/wiki/Line–sphere_intersection
    //
    // Find smallest real alpha such that: origin + alpha * direction is on the unit circle.
    //
    float oo = dot(origin, origin);
    float uo = dot(direction, origin);
    float uu = dot(direction, direction);
    float discriminant = uo*uo - uu * (oo - 1);

    // Early abort if a solution does not exist.
    // This check can be omitted, but it is adventageous to keep it for improved performance.
    if (discriminant < 0)
    {
        return NaN;
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

    if (isnan(alpha))
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

    float u = 0.5 + 0.5 * atan(cylinder_hit.x, cylinder_hit.y) / PI;
    float v = 0.5 + cylinder_hit.z;

    fragment_color = texture(my_texture, vec2(u, v));

    vec4 proj = projection_matrix * view_matrix * model_matrix * vec4(cylinder_hit, 1);
    float depth = (proj.z / proj.w);

    gl_FragDepth = 0.5 + 0.5 * depth;
}

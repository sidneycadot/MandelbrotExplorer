
#version 410 core

layout(location = 0) out vec4 fragment_color;

uniform uvec2 window_size;
uniform uint  frame_counter;

// Where are we?

uniform uint max_iterations;

uniform dvec2  map_center;
uniform double map_scale;
uniform double map_angle;

uint mandelbrot(double x0, double y0, uint max_iterations)
{
    double x = 0.0;
    double y = 0.0;

    uint iteration = 0;
    while (iteration < max_iterations)
    {
        double xx = x * x;
        double yy = y * y;

        if (xx + yy > 4.0)
        {
            break;
        }
        double xtemp = xx - yy + x0;
        y = 2 * x * y + y0;
        x = xtemp;
        ++iteration;
    }
    return iteration;
}

void main()
{
    double sx = gl_FragCoord.x;
    double sy = gl_FragCoord.y;

    // "outside" = (0, 0) -- (640, 480)

    // bottom-left pixel has (wx, wy) == (0.5, 0.5)
    // top-right pixel has (wx, wy) = 639.5, 479.5)

    uint width  = window_size.x;
    uint height = window_size.y;

    double scale = map_scale / min(width, height);

    float angle = radians(float(map_angle));

    double sin_angle = sin(angle);
    double cos_angle = cos(angle);

    double x = map_center.x + 0.5 * scale * (height * sin_angle + 2.0 * cos_angle * sx - 2.0 * sin_angle * sy - cos_angle * width);
    double y = map_center.y - 0.5 * scale * (cos_angle * (height - 2 * sy) + sin_angle * (-2 * sx + width));

    uint m = mandelbrot(x, y, max_iterations);

    if (m == max_iterations)
    {
        fragment_color = vec4(0.0, 0.0, 0.0, 1.0);
    }
    else
    {
        m = (m - frame_counter) % max_iterations;

        uint r = (m % 256);
        uint g = (m %  16) * 16;
        uint b = (m %   4) * 64;

        fragment_color = vec4(r / 255.0, g / 255.0, b / 255.0, 1.0);
    }
}


import math
import numpy as np


def normalize(v):
    return v / np.linalg.norm(v)


def _make_unit_sphere_triangles_recursive(triangle, recursion_level: int):
    if recursion_level == 0:
        return [triangle]

    (v1, v2, v3) = triangle

    v12 = normalize(v1 + v2)
    v13 = normalize(v1 + v3)
    v23 = normalize(v2 + v3)

    triangles = []

    triangles.extend(_make_unit_sphere_triangles_recursive((v1, v12, v13), recursion_level - 1))
    triangles.extend(_make_unit_sphere_triangles_recursive((v12, v2, v23), recursion_level - 1))
    triangles.extend(_make_unit_sphere_triangles_recursive((v12, v23, v13), recursion_level - 1))
    triangles.extend(_make_unit_sphere_triangles_recursive((v13, v23, v3), recursion_level - 1))

    return triangles


def make_unit_sphere_triangles(recursion_level: int):

    v1 = normalize(np.array((-1.0, -1.0, -1.0)))
    v2 = normalize(np.array((+1.0, +1.0, -1.0)))
    v3 = normalize(np.array((+1.0, -1.0, +1.0)))
    v4 = normalize(np.array((-1.0, +1.0, +1.0)))

    t1 = (v1, v2, v3)
    t2 = (v1, v4, v2)
    t3 = (v1, v3, v4)
    t4 = (v2, v4, v3)

    triangles = []

    triangles.extend(_make_unit_sphere_triangles_recursive(t1, recursion_level))
    triangles.extend(_make_unit_sphere_triangles_recursive(t2, recursion_level))
    triangles.extend(_make_unit_sphere_triangles_recursive(t3, recursion_level))
    triangles.extend(_make_unit_sphere_triangles_recursive(t4, recursion_level))

    return triangles


def make_unit_sphere_triangles_v2(recursion_level: int):

    Q = math.sqrt(5)
    R = math.sqrt((5 - Q)/10)
    S = math.sqrt((5 + Q)/10)

    vertices = [
        np.array((       0   , 0,  -1  )),
        np.array((       0   , 0,   1  )),
        np.array((    -2/Q   , 0,  -1/Q)),
        np.array((     2/Q   , 0,   1/Q)),
        np.array((( 5 + Q)/10, -R, -1/Q)),
        np.array((( 5 + Q)/10,  R, -1/Q)),
        np.array(((-5 - Q)/10, -R,  1/Q)),
        np.array(((-5 - Q)/10,  R,  1/Q)),
        np.array(((-5 + Q)/10, -S, -1/Q)),
        np.array(((-5 + Q)/10,  S, -1/Q)),
        np.array((( 5 - Q)/10, -S,  1/Q)),
        np.array((( 5 - Q)/10,  S,  1/Q))
    ]

    face_definitions = [
        (1, 11, 7),
        (1, 7, 6),
        (1, 6, 10),
        (1, 10, 3),
        (1, 3, 11),
        (4, 8, 0),
        (5, 4, 0),
        (9, 5, 0),
        (2, 9, 0),
        (8, 2, 0),
        (11, 9, 7),
        (7, 2, 6),
        (6, 8, 10),
        (10, 4, 3),
        (3, 5, 11),
        (4, 10, 8),
        (5, 3, 4),
        (9, 11, 5),
        (2, 7, 9),
        (8, 6, 2)
    ]

    triangles = []

    for (v1_idx, v2_idx, v3_idx) in face_definitions:
        toplevel_triangle = (vertices[v1_idx], vertices[v2_idx], vertices[v3_idx])
        triangles.extend(_make_unit_sphere_triangles_recursive(toplevel_triangle, recursion_level))

    return triangles


def make_cylinder_triangles(subdivision_count) -> tuple[list, list]:

    zlo = -0.5
    zhi = +0.5

    normals = []
    triangles = []
    for i in range(subdivision_count):
        a0 = (i + 0) / subdivision_count * math.tau
        a1 = (i + 1) / subdivision_count * math.tau

        x0 = math.cos(a0)
        y0 = math.sin(a0)
        x1 = math.cos(a1)
        y1 = math.sin(a1)

        triangle = ((x0, y0, zlo), (x1, y1, zlo), (x0, y0, zhi))
        normal = ((x0, y0, 0), (x1, y1, 0), (x0, y0, 0))
        triangles.append(triangle)
        normals.append(normal)

        triangle = ((x1, y1, zlo), (x1, y1, zhi), (x0, y0, zhi))
        normal = ((x1, y1, 0), (x1, y1, 0), (x0, y0, 0))
        triangles.append(triangle)
        normals.append(normal)

    return (triangles, normals)

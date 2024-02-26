"""Several OpenGL utilities."""

import os

import math
import numpy as np

from OpenGL.GL import *


def make_shader(filename: str, shader_type):
    """Read a shader source from disk and compile it."""
    try:
        with open(filename, "rb") as fi:
            shader_source = fi.read()
    except FileNotFoundError:
        print("Shader source not found: {!r} from {!r}".format(filename, os.getcwd()))
        return None

    shader = None
    try:
        shader = glCreateShader(shader_type)

        print("Compiling shader: {!r} ...".format(filename))

        glShaderSource(shader, shader_source)
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if status != GL_TRUE:
            log = glGetShaderInfoLog(shader)
            print("Error while compiling shader:", repr(log))
            raise RuntimeError("Error while compiling shader.")

    except BaseException:
        if shader is not None:
            glDeleteShader(shader)
        raise  # Re-raise exception

    return shader


def create_opengl_program(prefix: str) -> tuple:

    shader_type_definitions = [
        ("v", GL_VERTEX_SHADER),
        ("g", GL_GEOMETRY_SHADER),
        ("f", GL_FRAGMENT_SHADER)
    ]

    shaders = []
    shader_program = None

    try:

        shader_program = glCreateProgram()

        for (letter, shader_type) in shader_type_definitions:
            shader = make_shader("{}_{}.glsl".format(prefix, letter), shader_type)
            if shader is not None:
                shaders.append(shader)

        for shader in shaders:
            glAttachShader(shader_program, shader)

        print("Linking shader program with {} shaders ...".format(len(shaders)))
        glLinkProgram(shader_program)
        status = glGetProgramiv(shader_program,  GL_LINK_STATUS)
        if status != GL_TRUE:
            log = glGetProgramInfoLog(shader_program)
            print("Error while linking shader program:", repr(log))
            raise RuntimeError("Error while linking shader program.")

        print("Shader program linked successfully.")

    except BaseException:
        if shader_program is not None:
            glDeleteProgram(shader_program)
        for shader in shaders:
            glDeleteShader(shader)
        raise  # Re-raise exception

    return shaders, shader_program


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

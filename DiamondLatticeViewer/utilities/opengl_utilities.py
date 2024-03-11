"""OpenGL utility functions."""

import os
import ctypes

import numpy as np

from .opengl_symbols import *


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


def define_vertex_attributes(vbo_dtype, enable_flag: bool):
    """Examine a numpy structured array dtype and declare and enable the corresponding vertex attributes."""

    for (attribute_index, field_info_tuple) in enumerate(vbo_dtype.fields.values()):

        field_dtype = field_info_tuple[0]
        field_offset = field_info_tuple[1]

        field_sub_dtype = field_dtype.subdtype
        if field_sub_dtype is None:
            raise RuntimeError("Expected array dtype")

        (field_item_dtype, field_shape) = field_sub_dtype

        if len(field_shape) != 1:
            raise RuntimeError("Expected shape with 1 element.")

        field_element_count = field_shape[0]
        if not (1 <= field_element_count <= 4):
            raise RuntimeError("Bad number of elements.")

        match field_item_dtype:
            case np.float32:
                glVertexAttribPointer(
                    attribute_index,
                    field_element_count,
                    GL_FLOAT,
                    GL_FALSE,
                    vbo_dtype.itemsize,
                    ctypes.c_void_p(field_offset)
                )
            case np.int32:
                glVertexAttribIPointer(
                    attribute_index,
                    field_element_count,
                    GL_INT,
                    vbo_dtype.itemsize,
                    ctypes.c_void_p(field_offset)
                )
            case _:
                raise RuntimeError("Unknown field type.")

        if enable_flag:
            glEnableVertexAttribArray(attribute_index)

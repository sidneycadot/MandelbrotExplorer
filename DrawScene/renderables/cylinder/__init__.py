
import os

import math
import numpy as np


from OpenGL.GL import *

from matrices import rotate, scale, apply_transform_to_vertices
from renderables.geometry import make_cylinder_triangles
from renderables.renderable import Renderable
from renderables.utilities import create_opengl_program


class RenderableCylinder(Renderable):

    def __init__(self, subdivision_count: int, m_xform=None):

        shader_source_path = os.path.join(os.path.dirname(__file__), "cylinder")

        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        self._mvp_location = glGetUniformLocation(self._shader_program, "mvp")

        triangles = make_cylinder_triangles(subdivision_count)

        print("triangles:", len(triangles))

        triangle_vertices = np.array(triangles).reshape(-1, 3)

        triangle_vertices = apply_transform_to_vertices(m_xform, triangle_vertices)

        self._num_points = len(triangle_vertices)

        print("triangle_vertices shape:", triangle_vertices.shape)

        vbo_dtype = np.dtype([
            ("a_vertex" , np.float32, 3),
            ("a_color"  , np.float32, 3)
        ])

        vbo_data = np.empty(dtype=vbo_dtype, shape=self._num_points)

        vbo_data["a_vertex"] = triangle_vertices
        vbo_data["a_color"] = np.repeat(np.random.uniform(0.0, 1.0, size=(self._num_points // 6, 3)), 6, axis=0)

        # Make Vertex Buffer Object (VBO)
        self._vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, GL_STATIC_DRAW)

        # Create a vertex array object (VAO)
        # If a GL_ARRAY_BUFFER is bound, it will be associated with the VAO.

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        # Defines the attribute with index 0 in the current VAO.

        attribute_index = 0  # 3D vertex coordinates
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(attribute_index)

        attribute_index = 1  # 3D colors
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(attribute_index)

        # Unbind VAO
        glBindVertexArray(0)

        # Unbind VBO.
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def close(self):

        if self._vao is not None:
            glDeleteVertexArrays(1, (self._vao,))
            self._vao = None

        if self._vbo is not None:
            glDeleteBuffers(1, (self._vbo, ))
            self._vbo = None

        if self._shader_program is not None:
            glDeleteProgram(self._shader_program)
            self._shader_program = None

        if self._shaders is not None:
            for shader in self._shaders:
                glDeleteShader(shader)
            self._shaders = None

    def render(self, m_xform):

        glUseProgram(self._shader_program)

        glUniformMatrix4fv(self._mvp_location, 1, GL_TRUE, m_xform.astype(np.float32))

        glDisable(GL_CULL_FACE)
        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, self._num_points)
        glDisable(GL_CULL_FACE)

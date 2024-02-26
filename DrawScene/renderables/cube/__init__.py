
import os

import numpy as np


from OpenGL.GL import *

from renderables.renderable import Renderable
from renderables.utilities import create_opengl_program


class RenderableCube(Renderable):

    def __init__(self):

        self._num_points = 8

        shader_source_path = os.path.join(os.path.dirname(__file__), "cube")

        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        self._mvp_location = glGetUniformLocation(self._shader_program, "mvp")

        vertex_data = np.array([
            (-0.5, -0.5, -0.5),
            (-0.5, -0.5, +0.5),
            (-0.5, +0.5, -0.5),
            (-0.5, +0.5, +0.5),
            (+0.5, -0.5, -0.5),
            (+0.5, -0.5, +0.5),
            (+0.5, +0.5, -0.5),
            (+0.5, +0.5, +0.5)
        ], dtype=np.float32)

        # Make Vertex Buffer Object (VBO)
        self._vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        # Create a vertex array object (VAO)
        # If a GL_ARRAY_BUFFER is bound, it will be associated with the VAO.

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        # Defines the attribute with index 0 in the current VAO.

        attribute_index = 0
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Enable attribute with location 0.
        glEnableVertexAttribArray(attribute_index)

        # Unbind VAO
        glBindVertexArray(0)

        # Unbind VBO.
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def __del__(self):
        if self._vao is not None:
            glDeleteVertexArrays(1, (self._vao,))
            self._vao = None

        if self._vbo is not None:
            glDeleteBuffers(1, (self._vbo, ))
            self._vbo = None

        if self._shader_program is not None:
            glDeleteProgram(self._shader_program)

        if self._shaders is not None:
            for shader in self._shaders:
                glDeleteShader(shader)
            self._shaders = None

    def render(self, m_xform):

        glUseProgram(self._shader_program)

        glUniformMatrix4fv(self._mvp_location, 1, GL_TRUE, m_xform.astype(np.float32))

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self._num_points)

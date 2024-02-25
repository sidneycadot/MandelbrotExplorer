
import os

from PIL import Image

import numpy as np

from OpenGL.GL import *

from renderables.renderable import Renderable
from renderables.sphere.sphere_triangles import make_sphere_triangles
from renderables.utilities import create_opengl_program


def normalize(v):
    return v / np.linalg.norm(v)


def make_unit_sphere_triangles_recursive(triangle, recursion_level: int):
    if recursion_level == 0:
        return [triangle]

    (v1, v2, v3) = triangle

    v12 = normalize(v1 + v2)
    v13 = normalize(v1 + v3)
    v23 = normalize(v2 + v3)

    triangles = []

    triangles.extend(make_unit_sphere_triangles_recursive((v1, v12, v13), recursion_level - 1))
    triangles.extend(make_unit_sphere_triangles_recursive((v12, v2, v23), recursion_level - 1))
    triangles.extend(make_unit_sphere_triangles_recursive((v12, v23, v13), recursion_level - 1))
    triangles.extend(make_unit_sphere_triangles_recursive((v13, v23, v3), recursion_level - 1))

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

    triangles.extend(make_unit_sphere_triangles_recursive(t1, recursion_level))
    triangles.extend(make_unit_sphere_triangles_recursive(t2, recursion_level))
    triangles.extend(make_unit_sphere_triangles_recursive(t3, recursion_level))
    triangles.extend(make_unit_sphere_triangles_recursive(t4, recursion_level))

    return triangles


class RenderableSphere(Renderable):

    def __init__(self):

        shader_source_path = os.path.join(os.path.dirname(__file__), "sphere")

        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        self._mvp_location = glGetUniformLocation(self._shader_program, "mvp")

        self._texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        texture_image_path = os.path.join(os.path.dirname(__file__), "earth.png")

        with Image.open(texture_image_path) as im:
            image = np.array(im)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.shape[1], image.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, image)

        triangles = make_unit_sphere_triangles(recursion_level=6)
        #triangles = make_sphere_triangles()

        print("triangles:", len(triangles))

        triangle_vertices = np.array(triangles, dtype=np.float32).reshape(-1, 3)

        print("triangle_vertices shape:", triangle_vertices.shape)

        vbo_dtype = np.dtype([
            ("vertex", np.float32, 3),
            ("texture_coordinate", np.float32, 2)
        ])

        vbo_data = np.empty(dtype=vbo_dtype, shape=(len(triangle_vertices)))

        vbo_data["vertex"] = triangle_vertices
        vbo_data["texture_coordinate"][:, 0] = 0.5 + 0.5 * np.arctan2(triangle_vertices[:, 0], triangle_vertices[:, 2]) / np.pi
        vbo_data["texture_coordinate"][:, 1] = 0.5 - 0.5 * triangle_vertices[:, 1]

        # Prevent texture coordinate wrap-around.
        vbo_data["texture_coordinate"][1::3, 0] = vbo_data["texture_coordinate"][0::3, 0] + (vbo_data["texture_coordinate"][1::3, 0] - vbo_data["texture_coordinate"][0::3, 0] + 0.5) % 1.0 - 0.5
        vbo_data["texture_coordinate"][2::3, 0] = vbo_data["texture_coordinate"][0::3, 0] + (vbo_data["texture_coordinate"][2::3, 0] - vbo_data["texture_coordinate"][0::3, 0] + 0.5) % 1.0 - 0.5

        self._num_points = len(vbo_data)

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
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(attribute_index)

        attribute_index = 1  # 2D texture coordinates
        glVertexAttribPointer(attribute_index, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(attribute_index)

        # Unbind VAO
        glBindVertexArray(0)

        # Unbind VBO.
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def __del__(self):
        if self._vao is not None:
            glDeleteVertexArrays(1, (self._vao, ))
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
        glDrawArrays(GL_TRIANGLES, 0, self._num_points)

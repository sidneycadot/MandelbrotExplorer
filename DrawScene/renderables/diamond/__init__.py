import itertools
import os

import numpy as np


from OpenGL.GL import *

from matrices import translate, apply_transform_to_vertices, scale, scale_xyz, rotate
from renderables.renderable import Renderable
from renderables.utilities import create_opengl_program
from renderables.geometry import make_unit_sphere_triangles_v2, make_cylinder_triangles, normalize


def make_joint_triangles(p1, p2, diameter):
    joint_triangles = make_cylinder_triangles(36)
    joint_triangles_vertices = np.array(joint_triangles).reshape(-1, 3)

    upvec = np.array((0.0, 0.0, 1.0))
    pvec = normalize(p2 - p1)

    rvec = np.cross(upvec, pvec)
    rangle = np.arccos(np.dot(upvec, pvec))

    if np.linalg.norm(rvec) == 0:
        if rangle > 0:
            m_rot = scale(1.0)
        else:
            m_rot = scale(-1.0)
    else:
        m_rot = rotate(rvec[0], rvec[1], rvec[2], rangle)

    m_xform = translate(p1[0], p1[1], p1[2]) @ m_rot @ scale_xyz(diameter, diameter, np.linalg.norm(p1 - p2)) @ translate(0, 0, 0.5)

    joint_triangles_vertices = apply_transform_to_vertices(m_xform, joint_triangles_vertices)

    return joint_triangles_vertices


class RenderableDiamond(Renderable):

    def __init__(self):

        shader_source_path = os.path.join(os.path.dirname(__file__), "diamond")

        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        self._mvp_location = glGetUniformLocation(self._shader_program, "mvp")

        vbo_dtype = np.dtype([
            ("a_vertex" , np.float32, 3),
            ("a_color"  , np.float32, 3)
        ])

        sphere_triangles = make_unit_sphere_triangles_v2(recursion_level=2)
        sphere_triangle_vertices = np.array(sphere_triangles).reshape(-1, 3)

        vbo_data_list = []

        minq = 0
        maxq = 3

        if False:
            # add central red sphere

            m_xform = translate(2, 2, 2) @ scale(0.4)
            current_sphere_triangle_vertices = apply_transform_to_vertices(m_xform, sphere_triangle_vertices)

            vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_sphere_triangle_vertices))
            vbo_data["a_vertex"] = current_sphere_triangle_vertices
            vbo_data["a_color"] = np.repeat(((1, 0, 0), ), len(current_sphere_triangle_vertices), axis=0)
            vbo_data_list.append(vbo_data)

        for (ix, iy, iz) in itertools.product(range(minq, maxq + 1), repeat=3):
            if (ix - iy) % 2 == 0 and (ix - iz) % 2 == 0 and (ix + iy + iz) % 4 < 2:

                m_xform = translate(ix, iy, iz) @ scale(0.3)
                current_sphere_triangle_vertices = apply_transform_to_vertices(m_xform, sphere_triangle_vertices)

                vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_sphere_triangle_vertices))
                vbo_data["a_vertex"] = current_sphere_triangle_vertices
                vbo_data["a_color"] = np.repeat(np.random.uniform(0.0, 1.0, size=(len(current_sphere_triangle_vertices) // 3, 3)), 3, axis=0)

                vbo_data_list.append(vbo_data)

                for (dx, dy, dz) in itertools.product((-1,1), repeat=3):

                    jx = ix + dx
                    jy = iy + dy
                    jz = iz + dz

                    if max(jx, jy, jz) > 3:
                        continue

                    if (jx - jy) % 2 == 0 and (jx - jz) % 2 == 0 and (jx + jy + jz) % 4 < 2:

                        p1 = np.array((ix, iy, iz))
                        p2 = np.array((jx, jy, jz))

                        print("@@", (ix, iy, iz), (jx, jy, jz))

                        current_joint_triangles = make_joint_triangles(p1, p2, 0.1)

                        vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_joint_triangles))
                        vbo_data["a_vertex"] = current_joint_triangles
                        vbo_data["a_color"] = np.repeat(np.random.uniform(0.0, 1.0, size=(len(current_joint_triangles) // 6, 3)), 6, axis=0)

                        vbo_data_list.append(vbo_data)

        vbo_data = np.concatenate(vbo_data_list)
        vbo_data_list.clear()

        self._num_points = len(vbo_data)
        print("diamond vertices:", self._num_points)

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

        glEnable(GL_CULL_FACE)
        glBindVertexArray(self._vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, self._num_points, 1000)
        glDisable(GL_CULL_FACE)

import itertools
import os

import numpy as np


from OpenGL.GL import *

from matrices import translate, apply_transform_to_vertices, scale, rotate, apply_transform_to_normals
from renderables.renderable import Renderable
from renderables.opengl_utilities import create_opengl_program
from renderables.geometry import make_unit_sphere_triangles, make_cylinder_triangles, normalize, \
    make_unit_sphere_triangles_tetrahedron


def make_joint_triangles(p1, p2, diameter, subdivision_count):
    (joint_triangles, joint_normals) = make_cylinder_triangles(subdivision_count)
    joint_triangles_vertices = np.array(joint_triangles).reshape(-1, 3)
    joint_triangles_normals = np.array(joint_normals).reshape(-1, 3)

    upvec = np.array((0.0, 0.0, 1.0))
    pvec = normalize(p2 - p1)

    rvec = np.cross(upvec, pvec)
    rangle = np.arccos(np.dot(upvec, pvec))

    if np.linalg.norm(rvec) == 0:  # pvec is precisely parallel to upvec.
        if rangle > 0:
            m_rot = scale(+1.0)  # Identity matrix.
        else:
            m_rot = scale(-1.0)
    else:
        m_rot = rotate(rvec, rangle)

    # Get the requested cylinder from a unit cylinder by applying a translation, scaling, rotation, and translation.
    m_xform = translate((p1[0], p1[1], p1[2])) @ m_rot @ scale((diameter, diameter, np.linalg.norm(p1 - p2))) @ translate((0, 0, 0.5))

    joint_triangles_vertices = apply_transform_to_vertices(m_xform, joint_triangles_vertices)
    joint_triangles_normals = apply_transform_to_normals(m_xform, joint_triangles_normals)

    return (joint_triangles_vertices, joint_triangles_normals)


class RenderableDiamond(Renderable):

    def __init__(self):

        shader_source_path = os.path.join(os.path.dirname(__file__), "diamond")
        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        self._m_projection_location = glGetUniformLocation(self._shader_program, "m_projection")
        self._m_view_location = glGetUniformLocation(self._shader_program, "m_view")
        self._m_model_location = glGetUniformLocation(self._shader_program, "m_model")
        self._cells_per_dimension_location = glGetUniformLocation(self._shader_program, "cells_per_dimension")

        shader_source_path = os.path.join(os.path.dirname(__file__), "diamond_normals")
        (self._shaders2, self._shader_program2) = create_opengl_program(shader_source_path)

        self._m_projection_location2 = glGetUniformLocation(self._shader_program2, "m_projection")
        self._m_view_location2 = glGetUniformLocation(self._shader_program2, "m_view")
        self._m_model_location2 = glGetUniformLocation(self._shader_program2, "m_model")
        self._cells_per_dimension_location2 = glGetUniformLocation(self._shader_program, "cells_per_dimension")

        vbo_dtype = np.dtype([
            ("a_vertex" , np.float32, 3),
            ("a_normal" , np.float32, 3),
            ("a_color"  , np.float32, 3)
        ])

        sphere_triangles = make_unit_sphere_triangles(recursion_level=3)
        #sphere_triangles = make_unit_sphere_triangles_tetrahedron(recursion_level=3)
        sphere_triangle_vertices = np.array(sphere_triangles).reshape(-1, 3)
        sphere_triangle_normals = np.array(sphere_triangles).reshape(-1, 3)

        vbo_data_list = []

        add_red_center_spheres = False
        if add_red_center_spheres:
            # add central red sphere

            m_xform = translate((2, 2, 2)) @ scale(1.25)
            current_sphere_triangle_vertices = apply_transform_to_vertices(m_xform, sphere_triangle_vertices)
            current_sphere_triangle_normals = apply_transform_to_normals(m_xform, sphere_triangle_normals)

            vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_sphere_triangle_vertices))
            vbo_data["a_vertex"] = current_sphere_triangle_vertices
            vbo_data["a_normal"] = current_sphere_triangle_normals
            vbo_data["a_color"] = np.repeat(((1, 0, 0), ), len(current_sphere_triangle_vertices), axis=0)
            vbo_data_list.append(vbo_data)

        add_diamond_geometry = True
        if add_diamond_geometry:
            for (ix, iy, iz) in itertools.product(range(4), repeat=3):
                if (ix - iy) % 2 == 0 and (ix - iz) % 2 == 0 and (ix + iy + iz) % 4 < 2:

                    m_xform = translate((ix, iy, iz)) @ scale(0.3)

                    current_sphere_triangle_vertices = apply_transform_to_vertices(m_xform, sphere_triangle_vertices)
                    current_sphere_triangle_normals = apply_transform_to_normals(m_xform, sphere_triangle_normals)

                    vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_sphere_triangle_vertices))
                    vbo_data["a_vertex"] = current_sphere_triangle_vertices
                    vbo_data["a_normal"] = current_sphere_triangle_normals
                    vbo_data["a_color"] = np.repeat(np.random.uniform(0.0, 1.0, size=(len(current_sphere_triangle_vertices) // 3, 3)), 3, axis=0)

                    vbo_data_list.append(vbo_data)

                    for (dx, dy, dz) in itertools.product((-1, 1), repeat=3):

                        jx = ix + dx
                        jy = iy + dy
                        jz = iz + dz

                        if max(jx, jy, jz) > 3:
                            continue

                        if (jx - jy) % 2 == 0 and (jx - jz) % 2 == 0 and (jx + jy + jz) % 4 < 2:

                            p1 = np.array((ix, iy, iz))
                            p2 = np.array((jx, jy, jz))

                            (current_joint_triangles, current_joint_normals) = make_joint_triangles(p1, p2, 0.08, 36)

                            vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_joint_triangles))
                            vbo_data["a_vertex"] = current_joint_triangles
                            vbo_data["a_normal"] = current_joint_normals
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
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(attribute_index)

        attribute_index = 1  # 3D normals
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(attribute_index)

        attribute_index = 2  # 3D colors
        glVertexAttribPointer(attribute_index, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
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

    def render(self, m_projection, m_view, m_model):

        cells_per_dimension = 2

        if True:
            glUseProgram(self._shader_program)

            glUniformMatrix4fv(self._m_projection_location, 1, GL_TRUE, m_projection.astype(np.float32))
            glUniformMatrix4fv(self._m_view_location, 1, GL_TRUE, m_view.astype(np.float32))
            glUniformMatrix4fv(self._m_model_location, 1, GL_TRUE, m_model.astype(np.float32))
            glUniform1ui(self._cells_per_dimension_location, cells_per_dimension)

            glEnable(GL_CULL_FACE)
            glBindVertexArray(self._vao)
            glDrawArraysInstanced(GL_TRIANGLES, 0, self._num_points, cells_per_dimension ** 3)
            glDisable(GL_CULL_FACE)

        if False:
            glUseProgram(self._shader_program2)

            glUniformMatrix4fv(self._m_projection_location2, 1, GL_TRUE, m_projection.astype(np.float32))
            glUniformMatrix4fv(self._m_view_location2, 1, GL_TRUE, m_view.astype(np.float32))
            glUniformMatrix4fv(self._m_model_location2, 1, GL_TRUE, m_model.astype(np.float32))
            glUniform1ui(self._cells_per_dimension_location2, cells_per_dimension)

            glBindVertexArray(self._vao)
            glDrawArraysInstanced(GL_POINTS, 0, self._num_points, cells_per_dimension ** 3)

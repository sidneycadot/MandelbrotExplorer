"""This module implements the RenderableDiamondLattice class."""

import itertools
import os
from typing import Optional

import numpy as np

from utilities.matrices import translate, scale, apply_transform_to_vertices
from utilities.opengl_utilities import create_opengl_program, define_vertex_attributes
from utilities.opengl_imports import *
from utilities.geometry import make_unit_sphere_triangles, make_cylinder_triangles, make_cylinder_placement_transform

from renderables.renderable import Renderable


def in_diamond_lattice(ix: int, iy: int, iz: int) -> bool:
    """Return if a given integer (ix, iy, iz) coordinate is occupied in the diamond lattice."""
    return (ix % 2 == iy % 2 == iz % 2) and (ix + iy + iz) % 4 < 2


def make_diamond_lattice_unitcell_triangle_vertex_data():
    """Define triangles for the sphere and cylinder impostors that we will upload to the VBO."""

    # Make coarse unit sphere and unit cylinder triangle vertices.
    # These are used for the impostor hulls.

    sphere_triangles = make_unit_sphere_triangles(recursion_level=0)
    sphere_triangle_vertices = np.array(sphere_triangles).reshape(-1, 3)

    cylinder_triangles = make_cylinder_triangles(subdivision_count=6, capped=False)
    cylinder_triangle_vertices = np.array(cylinder_triangles).reshape(-1, 3)

    vbo_dtype = np.dtype([
        ("a_vertex", np.float32, 3),  # Triangle vertex
        ("a_lattice_position", np.int32, 3),  # Lattice position
        ("a_lattice_delta", np.int32, 3),  # Lattice delta (zero vector for sphere, nonzero vector for cylinder)
        ("inverse_placement_matrix_row1", np.float32, 4),  # Row 1 of inverse placement matrix.
        ("inverse_placement_matrix_row2", np.float32, 4),  # Row 2 of inverse placement matrix.
        ("inverse_placement_matrix_row3", np.float32, 4)  # Row 3 of inverse placement matrix.
    ])

    vbo_data_list = []

    for (ix, iy, iz) in itertools.product(range(4), repeat=3):
        if in_diamond_lattice(ix, iy, iz):

            placement_matrix = translate((ix, iy, iz)) @ scale(0.3)
            inverse_placement_matrix = np.linalg.inv(placement_matrix)

            impostor_hull_matrix = placement_matrix @ scale(1.26)

            impostor_triangle_vertices = apply_transform_to_vertices(impostor_hull_matrix, sphere_triangle_vertices)

            vbo_data = np.empty(dtype=vbo_dtype, shape=len(impostor_triangle_vertices))

            vbo_data["a_vertex"] = impostor_triangle_vertices
            vbo_data["a_lattice_position"] = (ix, iy, iz)
            vbo_data["a_lattice_delta"] = (0, 0, 0)
            vbo_data["inverse_placement_matrix_row1"] = inverse_placement_matrix[0]
            vbo_data["inverse_placement_matrix_row2"] = inverse_placement_matrix[1]
            vbo_data["inverse_placement_matrix_row3"] = inverse_placement_matrix[2]

            vbo_data_list.append(vbo_data)

            for (dx, dy, dz) in itertools.product((-1, 1), repeat=3):

                jx = ix + dx
                jy = iy + dy
                jz = iz + dz

                if max(jx, jy, jz) > 3:
                    continue

                if in_diamond_lattice(jx, jy, jz):
                    p1 = np.array((ix, iy, iz))
                    p2 = np.array((jx, jy, jz))

                    placement_matrix = make_cylinder_placement_transform(p1, p2, 0.10)
                    inverse_placement_matrix = np.linalg.inv(placement_matrix)

                    impostor_hull_matrix = placement_matrix @ scale((1.1, 1.1, 1.01))

                    current_bond_triangle_vertices = apply_transform_to_vertices(impostor_hull_matrix,
                                                                                 cylinder_triangle_vertices)

                    vbo_data = np.empty(dtype=vbo_dtype, shape=len(current_bond_triangle_vertices))
                    vbo_data["a_vertex"] = current_bond_triangle_vertices
                    vbo_data["a_lattice_position"] = (ix, iy, iz)
                    vbo_data["a_lattice_delta"] = (dx, dy, dz)
                    vbo_data["inverse_placement_matrix_row1"] = inverse_placement_matrix[0]
                    vbo_data["inverse_placement_matrix_row2"] = inverse_placement_matrix[1]
                    vbo_data["inverse_placement_matrix_row3"] = inverse_placement_matrix[2]

                    vbo_data_list.append(vbo_data)

    vbo_data = np.concatenate(vbo_data_list)

    return vbo_data


class RenderableDiamondLattice(Renderable):

    """A Renderable that renders a diamond crystal lattice using sphere and cylinder impostors."""

    def __init__(self, name: Optional[str] = None):

        super().__init__(name)

        # Variables that are used to communicate with the shaders.

        self.color_mode = 0
        self.cut_mode = 0
        self.unit_cells_per_dimension = 5
        self.crystal_side_length = 16.0
        self.impostor_mode = 0

        # Compile the shader program.

        shader_source_path = os.path.join(os.path.dirname(__file__), "diamond_lattice")
        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        # Find the location of uniform shader program variables.

        self._projection_matrix_location = glGetUniformLocation(self._shader_program, "projection_matrix")
        self._transposed_inverse_view_matrix_location = glGetUniformLocation(self._shader_program, "transposed_inverse_view_matrix")
        self._projection_view_model_matrix_location = glGetUniformLocation(self._shader_program, "projection_view_model_matrix")
        self._view_model_matrix_location = glGetUniformLocation(self._shader_program, "view_model_matrix")
        self._inverse_view_model_matrix_location = glGetUniformLocation(self._shader_program, "inverse_view_model_matrix")
        self._transposed_inverse_view_model_matrix_location = glGetUniformLocation(self._shader_program, "transposed_inverse_view_model_matrix")

        self._unit_cells_per_dimension_location = glGetUniformLocation(self._shader_program, "unit_cells_per_dimension")
        self._crystal_side_length_location = glGetUniformLocation(self._shader_program, "crystal_side_length")
        self._cut_mode_location = glGetUniformLocation(self._shader_program, "cut_mode")
        self._color_mode_location = glGetUniformLocation(self._shader_program, "color_mode")
        self._impostor_mode_location = glGetUniformLocation(self._shader_program, "impostor_mode")

        vbo_data = make_diamond_lattice_unitcell_triangle_vertex_data()

        print("Diamond lattice unit cell size: {} triangles, {} vertices, {} bytes ({} bytes per triangle).".format(
            vbo_data.size // 3, vbo_data.size, vbo_data.nbytes, vbo_data.itemsize))

        self._vertex_count = vbo_data.size

        # Make Vertex Buffer Object (VBO)
        self._vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, GL_STATIC_DRAW)

        # Create a vertex array object (VAO)
        # If a GL_ARRAY_BUFFER is bound, it will be associated with the VAO.

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        # Define attributes based on the vbo_data element type and enable them.
        define_vertex_attributes(vbo_data.dtype, True)

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

        glUseProgram(self._shader_program)

        glUniformMatrix4fv(self._projection_matrix_location, 1, GL_TRUE, m_projection.astype(np.float32))
        glUniformMatrix4fv(self._transposed_inverse_view_matrix_location, 1, GL_TRUE, np.linalg.inv(m_view).T.astype(np.float32))
        glUniformMatrix4fv(self._projection_view_model_matrix_location, 1, GL_TRUE, (m_projection @ m_view @ m_model).astype(np.float32))
        glUniformMatrix4fv(self._view_model_matrix_location, 1, GL_TRUE, (m_view @ m_model).astype(np.float32))
        glUniformMatrix4fv(self._inverse_view_model_matrix_location, 1, GL_TRUE, np.linalg.inv(m_view @ m_model).astype(np.float32))

        glUniformMatrix4fv(self._transposed_inverse_view_model_matrix_location, 1, GL_TRUE, np.linalg.inv(m_view @ m_model).T.astype(np.float32))

        glUniform1ui(self._unit_cells_per_dimension_location, self.unit_cells_per_dimension)
        glUniform1ui(self._color_mode_location, self.color_mode)
        glUniform1f(self._crystal_side_length_location, self.crystal_side_length)
        glUniform1ui(self._cut_mode_location, self.cut_mode)
        glUniform1ui(self._impostor_mode_location, self.impostor_mode)

        glEnable(GL_CULL_FACE)
        glBindVertexArray(self._vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, self._vertex_count, self.unit_cells_per_dimension ** 3)

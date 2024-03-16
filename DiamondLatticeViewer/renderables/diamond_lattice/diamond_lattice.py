"""This module implements the RenderableDiamondLattice class."""

import itertools
import os

import numpy as np

from utilities.matrices import translate, scale, apply_transform_to_vertices
from utilities.opengl_utilities import create_opengl_program, define_vertex_attributes, glGetUniformLocation_checked
from utilities.opengl_symbols import *
from utilities.geometry import (make_unit_sphere_triangles, make_unit_cylinder_triangles,
                                make_cylinder_placement_transform, normalize)

from renderables.renderable import Renderable
from utilities.world import World


def in_diamond_lattice(ix: int, iy: int, iz: int) -> bool:
    """Return if a given integer (ix, iy, iz) coordinate is occupied in the diamond lattice."""
    return (ix % 2 == iy % 2 == iz % 2) and (ix + iy + iz) % 4 < 2


def make_diamond_lattice_unitcell_triangle_vertex_data(transformation_matrix=None):
    """Define triangles for the sphere and cylinder impostors that we will upload to the VBO."""

    if transformation_matrix is None:
        transformation_matrix = np.identity(4)

    carbon_sphere_scale = 0.3
    carbon_carbon_bond_scale = 0.1

    # Make coarse unit sphere and unit cylinder triangle vertices.
    # These are used for the impostor hulls.

    unit_sphere_triangles = make_unit_sphere_triangles(recursion_level=0)
    unit_sphere_triangle_vertices = np.array(unit_sphere_triangles).reshape(-1, 3)

    unit_cylinder_triangles = make_unit_cylinder_triangles(subdivision_count=6, capped=False)
    unit_cylinder_triangle_vertices = np.array(unit_cylinder_triangles).reshape(-1, 3)

    # Prepare VBO data.

    vbo_dtype = np.dtype([
        ("a_vertex", np.float32, 3),  # Triangle vertex
        ("a_lattice_position", np.int32, 3),  # Lattice position
        ("a_lattice_delta", np.int32, 3),  # Lattice delta (zero vector for sphere, nonzero vector for cylinder)
        ("inverse_placement_matrix_row1", np.float32, 4),  # Row 1 of inverse placement matrix.
        ("inverse_placement_matrix_row2", np.float32, 4),  # Row 2 of inverse placement matrix.
        ("inverse_placement_matrix_row3", np.float32, 4)  # Row 3 of inverse placement matrix.
    ])

    vbo_data_list = []

    sphere_impostor_scale_matrix = scale(1.26)
    cylinder_impostor_scale_matrix = scale((1.2, 1.2, 1.01))

    for (ix, iy, iz) in itertools.product(range(4), repeat=3):
        if in_diamond_lattice(ix, iy, iz):

            # Add triangles for a single Carbon sphere.

            sphere_placement_matrix = translate((ix, iy, iz)) @ scale(carbon_sphere_scale)
            inverse_sphere_placement_matrix = np.linalg.inv(sphere_placement_matrix)

            sphere_impostor_triangle_vertices = apply_transform_to_vertices(
                sphere_placement_matrix @ sphere_impostor_scale_matrix, unit_sphere_triangle_vertices)

            vbo_data = np.empty(dtype=vbo_dtype, shape=len(sphere_impostor_triangle_vertices))

            vbo_data["a_vertex"] = sphere_impostor_triangle_vertices
            vbo_data["a_lattice_position"] = (ix, iy, iz)
            vbo_data["a_lattice_delta"] = (0, 0, 0)
            vbo_data["inverse_placement_matrix_row1"] = inverse_sphere_placement_matrix[0]
            vbo_data["inverse_placement_matrix_row2"] = inverse_sphere_placement_matrix[1]
            vbo_data["inverse_placement_matrix_row3"] = inverse_sphere_placement_matrix[2]

            vbo_data_list.append(vbo_data)

            for (dx, dy, dz) in itertools.product((-1, 1), repeat=3):

                jx = ix + dx
                jy = iy + dy
                jz = iz + dz

                if max(jx, jy, jz) > 3:
                    continue

                if in_diamond_lattice(jx, jy, jz):

                    # Add triangles for a single Carbon-Carbon bond cylinder.

                    c1 = np.array((ix, iy, iz))
                    c2 = np.array((jx, jy, jz))

                    # The bond cylinder doesn't have to go from the center of one carbon sphere to the center of
                    # the next carbon sphere; instead, it can go from the intersection of the bond cylinder with
                    # the first carbon sphere to the intersection of the bond cylinder with the second carbon sphere.
                    #
                    # This optimization makes the cylinder smaller, thereby decreasing the number
                    # of fragment shader runs.
                    #
                    # We subtract 98% of the nominal 'touching' value to make sure that the cylinder pierces
                    # the carbon spheres by a very small amount, thus preventing seams.

                    subtract = 0.98 * np.sqrt(carbon_sphere_scale ** 2 - carbon_carbon_bond_scale ** 2)

                    p1 = c2 + normalize(c1 - c2) * (np.linalg.norm(c1 - c2) - subtract)
                    p2 = c1 + normalize(c2 - c1) * (np.linalg.norm(c2 - c1) - subtract)

                    cylinder_placement_matrix = make_cylinder_placement_transform(p1, p2, carbon_carbon_bond_scale)
                    inverse_cylinder_placement_matrix = np.linalg.inv(cylinder_placement_matrix)

                    cylinder_impostor_triangle_vertices = apply_transform_to_vertices(
                        cylinder_placement_matrix @ cylinder_impostor_scale_matrix, unit_cylinder_triangle_vertices)

                    vbo_data = np.empty(dtype=vbo_dtype, shape=len(cylinder_impostor_triangle_vertices))
                    vbo_data["a_vertex"] = cylinder_impostor_triangle_vertices
                    vbo_data["a_lattice_position"] = (ix, iy, iz)
                    vbo_data["a_lattice_delta"] = (dx, dy, dz)
                    vbo_data["inverse_placement_matrix_row1"] = inverse_cylinder_placement_matrix[0]
                    vbo_data["inverse_placement_matrix_row2"] = inverse_cylinder_placement_matrix[1]
                    vbo_data["inverse_placement_matrix_row3"] = inverse_cylinder_placement_matrix[2]

                    vbo_data_list.append(vbo_data)

    vbo_data = np.concatenate(vbo_data_list)

    return vbo_data


class RenderableDiamondLattice(Renderable):

    """A Renderable that renders a diamond crystal lattice using sphere and cylinder impostors."""

    def __init__(self, world: World):

        # Variables that are used to communicate with the shaders.

        self._world = world

        self.color_mode = 0
        self.cut_mode = 0
        self.unit_cells_per_dimension = 5
        self.crystal_side_length = 16.0

        # Compile the shader program.

        shader_source_path = os.path.join(os.path.dirname(__file__), "diamond_lattice")
        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        # Find the location of uniform shader program variables.

        self._projection_matrix_location = glGetUniformLocation_checked(self._shader_program, "projection_matrix")
        self._transposed_inverse_view_matrix_location = glGetUniformLocation_checked(self._shader_program, "transposed_inverse_view_matrix")
        self._projection_view_model_matrix_location = glGetUniformLocation_checked(self._shader_program, "projection_view_model_matrix")
        self._view_model_matrix_location = glGetUniformLocation_checked(self._shader_program, "view_model_matrix")
        self._transposed_inverse_view_model_matrix_location = glGetUniformLocation_checked(self._shader_program, "transposed_inverse_view_model_matrix")

        self._unit_cells_per_dimension_location = glGetUniformLocation(self._shader_program, "unit_cells_per_dimension")
        self._crystal_side_length_location = glGetUniformLocation(self._shader_program, "crystal_side_length")
        self._cut_mode_location = glGetUniformLocation(self._shader_program, "cut_mode")
        self._color_mode_location = glGetUniformLocation(self._shader_program, "color_mode")
        self._impostor_mode_location = glGetUniformLocation(self._shader_program, "impostor_mode")

        # Make vertex buffer data.

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

    def render(self, projection_matrix, view_matrix, model_matrix):

        world = self._world

        glUseProgram(self._shader_program)

        glUniformMatrix4fv(self._projection_matrix_location, 1, GL_TRUE, projection_matrix.astype(np.float32))
        glUniformMatrix4fv(self._transposed_inverse_view_matrix_location, 1, GL_TRUE, np.linalg.inv(view_matrix).T.astype(np.float32))
        glUniformMatrix4fv(self._projection_view_model_matrix_location, 1, GL_TRUE, (projection_matrix @ view_matrix @ model_matrix).astype(np.float32))
        glUniformMatrix4fv(self._view_model_matrix_location, 1, GL_TRUE, (view_matrix @ model_matrix).astype(np.float32))

        glUniformMatrix4fv(self._transposed_inverse_view_model_matrix_location, 1, GL_TRUE, np.linalg.inv(view_matrix @ model_matrix).T.astype(np.float32))

        glUniform1ui(self._unit_cells_per_dimension_location, self.unit_cells_per_dimension)
        glUniform1ui(self._color_mode_location, self.color_mode)
        glUniform1f(self._crystal_side_length_location, self.crystal_side_length)
        glUniform1ui(self._cut_mode_location, self.cut_mode)

        glUniform1ui(self._impostor_mode_location, world.get_variable("impostor_mode"))

        glEnable(GL_CULL_FACE)
        glBindVertexArray(self._vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, self._vertex_count, self.unit_cells_per_dimension ** 3)

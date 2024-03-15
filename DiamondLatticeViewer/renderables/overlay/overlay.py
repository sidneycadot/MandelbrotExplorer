"""This module implements the RenderableOverlay class."""

import os

from PIL import Image, ImageDraw, ImageFont

import numpy as np

from utilities.opengl_symbols import *
from renderables.renderable import Renderable
from utilities.opengl_utilities import create_opengl_program, define_vertex_attributes


def make_overlay_vertex_data():

    triangles = [
        ((-1, -1), (1, -1), (1, 1)),
        ((-1, 1), (-1, -1), (+1, +1))
    ]

    triangle_vertices = np.array(triangles).reshape(-1, 2)

    vbo_dtype = np.dtype([
        ("a_vertex", np.float32, 2),
        ("a_brightness", np.float32)
    ])

    vbo_data = np.empty(dtype=vbo_dtype, shape=len(triangle_vertices))

    vbo_data["a_vertex"] = triangle_vertices
    vbo_data["a_brightness"] = 0.4

    return vbo_data


class RenderableOverlay(Renderable):

    def __init__(self, world):

        self._world = world
        self._last_text = None

        # Compile the shader program.

        shader_source_path = os.path.join(os.path.dirname(__file__), "overlay")
        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        # Find the location of uniform shader program variables.

        #self._model_matrix_location = glGetUniformLocation(self._shader_program, "model_matrix")
        #self._view_matrix_location = glGetUniformLocation(self._shader_program, "view_matrix")
        #self._projection_matrix_location = glGetUniformLocation(self._shader_program, "projection_matrix")

        #self._view_model_matrix_location = glGetUniformLocation(self._shader_program, "view_model_matrix")
        self._frame_buffer_size_location = glGetUniformLocation(self._shader_program, "frame_buffer_size")
        self._projection_view_model_matrix_location = glGetUniformLocation(self._shader_program, "projection_view_model_matrix")
        #self._inverse_view_model_matrix_location = glGetUniformLocation(self._shader_program, "inverse_view_model_matrix")
        #self._transposed_inverse_view_matrix_location = glGetUniformLocation(self._shader_program, "transposed_inverse_view_matrix")
        #self._transposed_inverse_view_model_matrix_location = glGetUniformLocation(self._shader_program, "transposed_inverse_view_model_matrix")
        #self._transposed_inverse_projection_view_model_matrix_location = glGetUniformLocation(self._shader_program, "transposed_inverse_projection_view_model_matrix")

        # Make vertex buffer data.

        vbo_data = make_overlay_vertex_data()

        print("Sphere impostor size: {} triangles, {} vertices, {} bytes ({} bytes per triangle).".format(
            vbo_data.size // 3, vbo_data.size, vbo_data.nbytes, vbo_data.itemsize))

        self._vertex_count = vbo_data.size

        # Make texture.

        self._texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        #glBindTexture(GL_TEXTURE_2D, self._texture)
        #with Image.new("RGBA", (512, 256), "red") as im:
        #    draw = ImageDraw.Draw(im)
        #    draw.ellipse(((100, 100), (200, 200)), fill='yellow', outline='blue', width=5)
        #    with Image.new("L", (512, 256), "black") as im_alpha:
        #        draw = ImageDraw.Draw(im_alpha)
        #        draw.ellipse(((150, 150), (250, 250)), fill='black', outline='white', width=5)
        #        im.putalpha(im_alpha)
        #        # Convert to numpy array
        #    image = np.array(im)

        #glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.shape[1], image.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        #glGenerateMipmap(GL_TEXTURE_2D)

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
            glDeleteVertexArrays(1, (self._vao, ))
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

        #glUniformMatrix4fv(self._model_matrix_location, 1, GL_TRUE, model_matrix.astype(np.float32))
        #glUniformMatrix4fv(self._view_matrix_location, 1, GL_TRUE, view_matrix.astype(np.float32))
        #glUniformMatrix4fv(self._projection_matrix_location, 1, GL_TRUE, projection_matrix.astype(np.float32))

        #glUniformMatrix4fv(self._view_model_matrix_location, 1, GL_TRUE, (view_matrix @ model_matrix).astype(np.float32))
        glUniformMatrix4fv(self._projection_view_model_matrix_location, 1, GL_TRUE, (projection_matrix @ view_matrix @ model_matrix).astype(np.float32))
        #glUniformMatrix4fv(self._inverse_view_model_matrix_location, 1, GL_TRUE, np.linalg.inv(view_matrix @ model_matrix).astype(np.float32))
        #glUniformMatrix4fv(self._transposed_inverse_view_matrix_location, 1, GL_TRUE, np.linalg.inv(view_matrix).T.astype(np.float32))
        #glUniformMatrix4fv(self._transposed_inverse_view_model_matrix_location, 1, GL_TRUE, np.linalg.inv(view_matrix @ model_matrix).T.astype(np.float32))
        #glUniformMatrix4fv(self._transposed_inverse_projection_view_model_matrix_location, 1, GL_TRUE, np.linalg.inv(projection_matrix @ view_matrix @ model_matrix).T.astype(np.float32))

        (framebuffer_width, framebuffer_height) = world.get_variable("framebuffer_size")

        glBindTexture(GL_TEXTURE_2D, self._texture)

        text = "render distance: {}\nframebuffer size: {}\nrender time per frame: {:.3f} ms".format(
            world.get_variable("render_distance"),
            (framebuffer_width, framebuffer_height),
            world.get_variable("ms_per_frame")
        )

        if text != self._last_text:
            font = ImageFont.load_default(size=16.0)
            with Image.new("RGBA", (framebuffer_width, framebuffer_height), (255, 255, 255, 0)) as im:
                draw = ImageDraw.Draw(im)
                draw.multiline_text((10, 4), text, font=font, fill='yellow')
                image = np.array(im)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.shape[1], image.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        glUniform2ui(self._frame_buffer_size_location, framebuffer_width, framebuffer_height)

        glBindVertexArray(self._vao)

        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)

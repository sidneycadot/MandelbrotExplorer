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
        ("a_vertex", np.float32, 2)
    ])

    vbo_data = np.empty(dtype=vbo_dtype, shape=len(triangle_vertices))

    vbo_data["a_vertex"] = triangle_vertices

    return vbo_data


class RenderableOverlay(Renderable):

    def __init__(self, world):

        self._world = world

        # Compile the shader program.

        shader_source_path = os.path.join(os.path.dirname(__file__), "overlay")
        (self._shaders, self._shader_program) = create_opengl_program(shader_source_path)

        # Find the location of uniform shader program variables.

        self._frame_buffer_size_location = glGetUniformLocation(self._shader_program, "frame_buffer_size")
        self._projection_view_model_matrix_location = glGetUniformLocation(self._shader_program, "projection_view_model_matrix")

        # Make vertex buffer data.

        vbo_data = make_overlay_vertex_data()

        print("Overlay size: {} triangles, {} vertices, {} bytes ({} bytes per triangle).".format(
            vbo_data.size // 3, vbo_data.size, vbo_data.nbytes, vbo_data.itemsize))

        self._vertex_count = vbo_data.size

        # Prepare texture.

        truetype_font_source_path = os.path.join(os.path.dirname(__file__), "Monoid-Regular.ttf")
        truetype_font_size = 12

        self._last_text = None
        self._font = ImageFont.truetype(truetype_font_source_path, truetype_font_size)
        self._texture_background = (40, 70, 200, 64)
        self._texture_image = Image.new("RGBA", (300, 80), self._texture_background)
        self._texture_draw = ImageDraw.Draw(self._texture_image)

        self._texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            self._texture_image.size[0], self._texture_image.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE,
            self._texture_image.tobytes()
        )

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

        if self._texture is not None:
            glDeleteTextures(1, (self._texture, ))

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

        glUniformMatrix4fv(
            self._projection_view_model_matrix_location, 1, GL_TRUE,
            (projection_matrix @ view_matrix @ model_matrix).astype(np.float32)
        )

        (framebuffer_width, framebuffer_height) = world.get_variable("framebuffer_size")

        # We need to inform the shader program about the size of the window we're rendering, so it can
        # re-scale the overlay texture to render at one texture pixel per framebuffer pixel.
        glUniform2ui(self._frame_buffer_size_location, framebuffer_width, framebuffer_height)

        glBindTexture(GL_TEXTURE_2D, self._texture)

        # Update the text we want to render.
        text = "diamond lattice side length: {}\nrender distance: {}\nframebuffer size: {}\nrender time per frame: {:.3f} ms".format(
            world.get_variable("diamond_lattice_side_length"),
            world.get_variable("render_distance"),
            (framebuffer_width, framebuffer_height),
            world.get_variable("ms_per_frame")
        )

        if text != self._last_text:
            # If the text has render the text and upload it to texture memory.
            self._texture_image.paste(
                self._texture_background,
                (0, 0, self._texture_image.size[0], self._texture_image.size[1])
            )
            self._texture_draw.multiline_text((10, 4), text, font=self._font, fill='yellow')
            glTexSubImage2D(
                GL_TEXTURE_2D, 0,
                0, 0,
                self._texture_image.size[0], self._texture_image.size[1],
                GL_RGBA, GL_UNSIGNED_BYTE, self._texture_image.tobytes()
            )
            self._last_text = text

        glBindVertexArray(self._vao)

        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)
        glDisable(GL_BLEND)

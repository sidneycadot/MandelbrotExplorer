#! /usr/bin/env python3

import contextlib

import glfw
from OpenGL.GL import *

from utilities import create_glfw_window, create_opengl_program
from matrices import translate, rotate, projection
from PIL import Image

import numpy as np


class Renderable:
    pass


class RenderableFloor(Renderable):

    def __init__(self, size):

        self._size = size

        self._shaders = None
        self._shader_program = None
        self._mvp_location = None
        self._vao = None
        self._vbo = None

    def open(self):

        (self._shaders, self._shader_program) = create_opengl_program("shaders/floor")

        self._mvp_location = glGetUniformLocation(self._shader_program, "mvp")

        vertex_data = np.array([
            (-0.5, -0.5),
            (-0.5, +0.5),
            (+0.5, -0.5),
            (+0.5, +0.5)
        ], dtype=np.float32)

        vertex_data *= self._size

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
        glVertexAttribPointer(attribute_index, 2, GL_FLOAT, GL_FALSE, 0, None)

        # Enable attribute with location 0.
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

        if self._shaders is not None:
            for shader in self._shaders:
                glDeleteShader(shader)
            self._shaders = None

    # noinspection PyUnusedLocal
    def render(self, t_now: float, m_xform):

        glUseProgram(self._shader_program)

        mvp = m_xform
        glUniformMatrix4fv(self._mvp_location, 1, GL_TRUE, mvp.astype(np.float32))

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)


class RenderableCube(Renderable):

    def __init__(self, x: float, y: float, z: float, scale: float, rotation_frequency: float):

        self._location = (x, y, z)
        self._scale = scale
        self._rotation_frequency = rotation_frequency

        self._shaders = None
        self._shader_program = None
        self._mvp_location = None
        self._vao = None
        self._vbo = None
        self._num_points = 8

    def open(self):

        (self._shaders, self._shader_program) = create_opengl_program("shaders/cube")

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

        vertex_data *= self._scale

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

    def close(self):
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

    def render(self, t_now, m_xform):

        glUseProgram(self._shader_program)

        m_model = translate(*self._location) @ rotate(0, 1, 0, t_now * self._rotation_frequency)

        mvp = m_xform @ m_model
        glUniformMatrix4fv(self._mvp_location, 1, GL_TRUE, mvp.astype(np.float32))

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self._num_points)


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

    t1 = (v1, v3, v2)
    t2 = (v1, v2, v4)
    t3 = (v1, v4, v3)
    t4 = (v2, v3, v4)

    triangles = []

    triangles.extend(make_unit_sphere_triangles_recursive(t1, recursion_level))
    triangles.extend(make_unit_sphere_triangles_recursive(t2, recursion_level))
    triangles.extend(make_unit_sphere_triangles_recursive(t3, recursion_level))
    triangles.extend(make_unit_sphere_triangles_recursive(t4, recursion_level))

    return triangles


class RenderableSphere(Renderable):

    def __init__(self, x: float, y: float, z: float, scale: float, revolution_frequency: float):

        self._location = (x, y, z)
        self._scale = scale
        self._revolution_frequency = revolution_frequency

        self._shaders = None
        self._shader_program = None
        self._mvp_location = None
        self._texture = None
        self._vao = None
        self._vbo = None
        self._num_points = None

    def open(self):

        (self._shaders, self._shader_program) = create_opengl_program("shaders/sphere")

        self._mvp_location = glGetUniformLocation(self._shader_program, "mvp")

        self._texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        with Image.open("earth.png") as im:
            image = np.array(im)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.shape[1], image.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, image)
        #glGenerateMipmap(GL_TEXTURE_2D)

        triangles = make_unit_sphere_triangles(recursion_level=6)

        triangle_vertices = np.array(triangles, dtype=np.float32).reshape(-1, 3)

        print("triangle_vertices shape:", triangle_vertices.shape)

        vbo_dtype = np.dtype([
            ("vertex", np.float32, 3),
            ("texture_coordinate", np.float32, 2)
        ])

        vbo_data = np.empty(dtype=vbo_dtype, shape=(len(triangle_vertices)))

        vbo_data["vertex"] = triangle_vertices * (0.5 * self._scale)
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

    def close(self):
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

    # noinspection PyUnusedLocal
    def render(self, t_now: float, m_xform):

        glUseProgram(self._shader_program)

        m_model = translate(*self._location) @ rotate(0, 1, 0, t_now * self._revolution_frequency)

        mvp = m_xform @ m_model
        glUniformMatrix4fv(self._mvp_location, 1, GL_TRUE, mvp.astype(np.float32))

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, self._num_points)


class RenderableScene(Renderable):

    def __init__(self):
        self._models = []

    def add_model(self, model):
        self._models.append(model)

    def open(self):
        for model in self._models:
            model.open()

    def close(self):
        for model in self._models:
            model.close()

    def render(self, t_now: float, m_xform):

        for model in self._models:
            model.render(t_now, m_xform)


class Application:

    def __init__(self):
        pass

    def run(self):
        """Main entry point."""

        with (contextlib.ExitStack() as exit_stack):

            glfw_version = glfw.get_version_string().decode()
            print(glfw_version)

            if not glfw.init():
                raise RuntimeError("Unable to initialize GLFW.")
            exit_stack.callback(glfw.terminate)

            # Create a GLFW window and set it as the current OpenGL context.

            window = create_glfw_window(exit_stack, 4, 1)

            glfw.set_framebuffer_size_callback(window, lambda *args: self.framebuffer_size_callback(*args))
            glfw.set_key_callback(window, lambda *args: self.key_callback(*args))

            glfw.make_context_current(window)

            glfw.swap_interval(1)

            # Create the scene model.
            scene = RenderableScene()
            for i in range(3):
                scene.add_model(RenderableSphere(3 * np.cos(i/3*2*np.pi), 0.5, 3 * np.sin(i/3*2*np.pi), 1.00, 1.5 + 2.5 * i))
            #scene.add_model(RenderableCube(-2.0, 0.15, 0.0, 0.30, 0.0))
            scene.add_model(RenderableFloor(8.0))
            scene.open()
            with contextlib.closing(scene):

                # Prepare loop.

                frame_counter = 0
                t_prev = None

                glPointSize(0.1)
                glClearColor(0.12, 0.12, 0.12, 1.0)
                glEnable(GL_DEPTH_TEST)

                while not glfw.window_should_close(window):

                    t_now = glfw.get_time()
                    if t_prev is not None:
                        frame_duration = (t_now - t_prev)
                        print("@@ {:20.4f} ms".format(frame_duration * 1000.0))
                    t_prev = t_now

                    # Make perspective projection matrix.

                    (framebuffer_width, framebuffer_height) = glfw.get_framebuffer_size(window)
                    fov_degrees = 30.0
                    near_plane = 0.5
                    far_plane = 50.0

                    m_projection = projection(framebuffer_width, framebuffer_height, fov_degrees, near_plane, far_plane)

                    # Make view (observer) matrix.

                    m_view = translate(0.0, -1.5, -10.0) @ rotate(0, 1, 0, t_now * -0.5)

                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                    scene.render(t_now,  m_projection @ m_view)

                    glfw.swap_buffers(window)
                    glfw.poll_events()
                    frame_counter += 1

    # noinspection PyMethodMayBeStatic
    def framebuffer_size_callback(self, _window, width, height):
        print("Resizing framebuffer:", width, height)
        glViewport(0, 0, width, height)

    def key_callback(self, window, key: int, scancode: int, action: int, mods: int):

        if action == glfw.PRESS:
            match key:
                case glfw.KEY_ESCAPE:
                    glfw.set_window_should_close(window, True)


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

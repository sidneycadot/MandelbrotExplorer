"""OpenGL Mandelbrot viewer."""

import math
import time
import contextlib
from enum import Enum

import numpy as np

import glfw
from OpenGL.GL import *


def video_mode_preference(mode) -> tuple[int, int]:
    return (mode.size.width * mode.size.height, mode.refresh_rate)


def create_glfw_fullscreen_window(exit_stack, monitor, version_major: int, version_minor: int):
    """Create a fullscreen window using GLFW."""

    # Find the best full-screen video mode.

    modes = glfw.get_video_modes(monitor)
    best_mode = modes[0]
    for mode in modes:
        if video_mode_preference(mode) > video_mode_preference(best_mode):
            best_mode = mode

    # Set up window creation hints.

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, version_major)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, version_minor)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    # Create the window.

    window = glfw.create_window(best_mode.size.width, best_mode.size.height, "Mandelbrot Viewer", monitor, None)
    if not window:
        raise RuntimeError("Unable to create window using GLFW.")
    exit_stack.callback(glfw.destroy_window, window)

    return window


def create_opengl_program(exit_stack):

    # vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    # exit_stack.callback(glDeleteShader, vertex_shader)

    # with open("vertex_shader.glsl", "rb") as fi:
    #     shader_source = fi.read()
    # glShaderSource(vertex_shader, shader_source)
    # glCompileShader(vertex_shader)
    # status = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    # if status != GL_TRUE:
    #     raise RuntimeError("Error while compiling the vertex shader.")

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    exit_stack.callback(glDeleteShader, fragment_shader)
    with open("fragment_shader.glsl", "rb") as fi:
        shader_source = fi.read()
    glShaderSource(fragment_shader, shader_source)

    glCompileShader(fragment_shader)
    status = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if status != GL_TRUE:
        raise RuntimeError("Error while compiling the fragment shader.")

    program = glCreateProgram()
    exit_stack.callback(glDeleteProgram, program)

    # glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)

    glLinkProgram(program)
    status = glGetProgramiv(program,  GL_LINK_STATUS)
    print("link status:", status)
    if status != GL_TRUE:
        raise RuntimeError("OpenGL program link error")

    return program


def create_opengl_vertex_array_object(exit_stack):

    # Prepare VBO.

    # define quad vertices
    vertex_data = np.array([
        -1.0, -1.0,
        +1.0, -1.0,
        -1.0, +1.0,
        +1.0, +1.0
    ], dtype=np.float32)

    # Make Vertex Buffer Object (VBO)
    vertex_buffer = glGenBuffers(1)
    exit_stack.callback(glDeleteBuffers, 1, (vertex_buffer, ))

    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    # Create a vertex array object (VAO)
    # If a GL_ARRAY_BUFFER is bound, it will be associated with the VAO.

    vao = glGenVertexArrays(1)
    exit_stack.callback(glDeleteVertexArrays, 1, (vao, ))

    glBindVertexArray(vao)

    # This defines how attribute with location 0 should be obtained from the current VBO.
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)

    # enable attribute with location 0.
    glEnableVertexAttribArray(0)

    # unbind VAO
    glBindVertexArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return vao


class ControlMode(Enum):
    MOVE_OBSERVER = 1
    MOVE_OBSERVED = 2


class MandelbrotRenderer:

    def __init__(self):
        self.map_center = (0.0, 0.0)
        self.map_scale = 4.0
        self.map_angle = 0.0
        self.max_iterations = 256
        self.control_mode = ControlMode.MOVE_OBSERVER

        self.window_size_shader_location = None
        self.frame_counter_shader_location = None
        self.map_center_shader_location = None
        self.map_scale_shader_location = None
        self.map_angle_shader_location = None
        self.max_iterations_shader_location = None

    def key_callback(self, window, key: int, scancode: int, action: int, mods: int):
        if action in (glfw.PRESS, glfw.REPEAT):
            match key:
                case glfw.KEY_RIGHT | glfw.KEY_D:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            angle = math.radians(self.map_angle)
                        case ControlMode.MOVE_OBSERVED:
                            angle = math.radians(self.map_angle + 180)
                    dx = 0.10 * math.cos(angle) * self.map_scale
                    dy = 0.10 * math.sin(angle) * self.map_scale
                    self.map_center = (self.map_center[0] + dx, self.map_center[1] + dy)
                    glUniform2d(self.map_center_shader_location, self.map_center[0], self.map_center[1])
                case glfw.KEY_UP | glfw.KEY_W:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            angle = math.radians(self.map_angle + 90)
                        case ControlMode.MOVE_OBSERVED:
                            angle = math.radians(self.map_angle + 270)
                    dx = 0.10 * math.cos(angle) * self.map_scale
                    dy = 0.10 * math.sin(angle) * self.map_scale
                    self.map_center = (self.map_center[0] + dx, self.map_center[1] + dy)
                    glUniform2d(self.map_center_shader_location, self.map_center[0], self.map_center[1])
                case glfw.KEY_LEFT | glfw.KEY_A:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            angle = math.radians(self.map_angle + 180)
                        case ControlMode.MOVE_OBSERVED:
                            angle = math.radians(self.map_angle)
                    dx = 0.10 * math.cos(angle) * self.map_scale
                    dy = 0.10 * math.sin(angle) * self.map_scale
                    self.map_center = (self.map_center[0] + dx, self.map_center[1] + dy)
                    glUniform2d(self.map_center_shader_location, self.map_center[0], self.map_center[1])
                case glfw.KEY_DOWN | glfw.KEY_S:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            angle = math.radians(self.map_angle + 270)
                        case ControlMode.MOVE_OBSERVED:
                            angle = math.radians(self.map_angle + 90)
                    dx = 0.10 * math.cos(angle) * self.map_scale
                    dy = 0.10 * math.sin(angle) * self.map_scale
                    self.map_center = (self.map_center[0] + dx, self.map_center[1] + dy)
                    glUniform2d(self.map_center_shader_location, self.map_center[0], self.map_center[1])
                case glfw.KEY_X:
                    self.map_scale *= 0.5
                    glUniform1d(self.map_scale_shader_location, self.map_scale)
                case glfw.KEY_Z:
                    self.map_scale *= 2.0
                    glUniform1d(self.map_scale_shader_location, self.map_scale)
                case glfw.KEY_C:
                    self.max_iterations = max(1, self.max_iterations // 2)
                    glUniform1ui(self.max_iterations_shader_location, self.max_iterations)
                case glfw.KEY_V:
                    self.max_iterations *= 2
                    glUniform1ui(self.max_iterations_shader_location, self.max_iterations)
                case glfw.KEY_LEFT_BRACKET:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            self.map_angle += 10
                        case ControlMode.MOVE_OBSERVED:
                            self.map_angle -= 10
                    glUniform1d(self.map_angle_shader_location, self.map_angle)
                case glfw.KEY_RIGHT_BRACKET:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            self.map_angle -= 10
                        case ControlMode.MOVE_OBSERVED:
                            self.map_angle += 10
                    glUniform1d(self.map_angle_shader_location, self.map_angle)
                case glfw.KEY_BACKSLASH:
                    self.map_angle = 0.0
                    glUniform1d(self.map_angle_shader_location, self.map_angle)

        if action == glfw.PRESS:
            match key:
                case glfw.KEY_SPACE:
                    match self.control_mode:
                        case ControlMode.MOVE_OBSERVER:
                            self.control_mode = ControlMode.MOVE_OBSERVED
                        case ControlMode.MOVE_OBSERVED:
                            self.control_mode = ControlMode.MOVE_OBSERVER
                case glfw.KEY_ESCAPE:
                    glfw.set_window_should_close(window, True)

        print("cx {} cy {} scale {} angle {} max {}".format(
            self.map_center[0], self.map_center[1],
            self.map_scale, self.map_angle, self.max_iterations))

    def framebuffer_size_callback(self, window, width: int, height: int):
        glViewport(0, 0, width, height)
        glUniform2ui(self.window_size_shader_location, width, height)

    def run(self):

        with contextlib.ExitStack() as exit_stack:

            glfw_version = glfw.get_version_string()
            print(glfw_version)

            if not glfw.init():
                raise RuntimeError("Unable to initialize GLFW.")
            exit_stack.callback(glfw.terminate)

            # Create a GLFW fullscreen window.

            window = create_glfw_fullscreen_window(exit_stack, glfw.get_primary_monitor(), 4, 2)

            # Make the new fullscreen window the current OpenGL context.

            glfw.make_context_current(window)

            # Create an OpenGL shader program and make it current.

            program = create_opengl_program(exit_stack)
            glUseProgram(program)

            # Get locations of all uniform variables

            self.window_size_shader_location = glGetUniformLocation(program, "window_size")
            self.frame_counter_shader_location = glGetUniformLocation(program, "frame_counter")
            self.map_center_shader_location = glGetUniformLocation(program, "map_center")
            self.map_scale_shader_location = glGetUniformLocation(program, "map_scale")
            self.map_angle_shader_location = glGetUniformLocation(program, "map_angle")
            self.max_iterations_shader_location = glGetUniformLocation(program, "max_iterations")

            # Register callbacks

            glfw.set_key_callback(window, lambda *args: self.key_callback(*args))
            glfw.set_framebuffer_size_callback(window, lambda *args: self.framebuffer_size_callback(*args))

            viewport = glGetIntegerv(GL_VIEWPORT)
            self.framebuffer_size_callback(window, viewport[2], viewport[3])

            glUniform2d(self.map_center_shader_location, self.map_center[0], self.map_center[1])
            glUniform1d(self.map_scale_shader_location, self.map_scale)
            glUniform1d(self.map_angle_shader_location, self.map_angle)
            glUniform1ui(self.max_iterations_shader_location, self.max_iterations)

            # Create OpenGL Vertex Array Object
            vao = create_opengl_vertex_array_object(exit_stack)

            # Set swap interval.

            glfw.swap_interval(1)

            # Prepare loop.

            frame_counter = 0
            t1 = time.monotonic()

            glClearColor(1.0, 1.0, 1.0, 1.0)

            while not glfw.window_should_close(window):

                glUniform1ui(self.frame_counter_shader_location, frame_counter)

                glBindVertexArray(vao)
                glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
                glBindVertexArray(0)

                glfw.swap_buffers(window)
                glfw.poll_events()
                frame_counter += 1

            t2 = time.monotonic()
            duration = (t2 - t1)
            print(frame_counter / duration)


def main():
    renderer = MandelbrotRenderer()
    renderer.run()


if __name__ == "__main__":
    main()

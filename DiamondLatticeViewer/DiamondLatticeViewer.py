#! /usr/bin/env python3

import numpy as np

import glfw

from utilities.opengl_symbols import *
from utilities.matrices import translate, rotate, scale, perspective_projection, multiply_matrices

from renderables import (RenderableScene, RenderableOptionalModel, RenderableModelTransformer, RenderableFloor,
                         RenderableSphereImpostor, RenderableCylinderImpostor, RenderableDiamondLattice)

from utilities.world import World


def make_scene(world: World) -> RenderableScene:
    """Create a scene in the given world."""

    scene = RenderableScene()

    # The floor model.

    world.set_variable("floor_enabled", True)
    scene.add_model(
        RenderableOptionalModel(
            RenderableModelTransformer(
                RenderableFloor(8.0, 8.0),
                lambda: translate((0, 0, 0))
            ),
            lambda: world.get_variable("floor_enabled")
        )
    )

    # The sphere impostor constellation.

    draw_sphere_impostor = False
    if draw_sphere_impostor:
        sphere_imposter_constellation = RenderableScene()

        earth = RenderableSphereImpostor("earth.png")

        sphere_imposter_constellation.add_model(
            RenderableModelTransformer(
                earth,
                lambda: multiply_matrices(
                    translate((+0.8, 0.0, 0)),
                    scale((1.0, 1.0, 1.0)),
                    rotate((0, 1, 0), 0 * world.time())
                )
            )
        )

        moon = RenderableSphereImpostor("moon.png")

        sphere_imposter_constellation.add_model(
            RenderableModelTransformer(
                moon,
                lambda: multiply_matrices(
                    translate((-0.8, 0.0, 0.3)),
                    scale((1.0, 1.0, 1.0)),
                    rotate((0, 1, 0), 0.0 * world.time())
                )
            )
        )

        scene.add_model(
            RenderableModelTransformer(
                sphere_imposter_constellation,
                lambda: multiply_matrices(
                    rotate((0, 1, 0), 1.0 * world.time())
                )
            )
        )

    # The cylinder impostor constellation.

    draw_cylinder_impostor = False
    if draw_cylinder_impostor:
        cylinder_impostor = RenderableCylinderImpostor()

        scene.add_model(
            RenderableModelTransformer(
                cylinder_impostor,
                lambda: multiply_matrices(
                    translate((+0.25, 0.0, 0)),
                    rotate((0, 1, 0), 0.0 * world.time()),
                    rotate((1, 0, 0), 0.5 * world.time()),
                    scale((0.2, 0.2, 4.0))
                )
            )
        )

        sphere_impostor = RenderableSphereImpostor("earth.png")

        scene.add_model(
            RenderableModelTransformer(
                sphere_impostor,
                lambda: multiply_matrices(
                    translate((+0.0, 0.0, 0)),
                    scale((1.0, 1.0, 1.0)),
                    rotate((0, 1, 0), 1 * world.time())
                )
            )
        )

    # The diamond lattice.

    diamond_lattice = RenderableDiamondLattice()
    world.set_variable("diamond_lattice", diamond_lattice)

    world.set_variable("diamond_lattice_enabled", True)
    scene.add_model(
        RenderableOptionalModel(
            RenderableModelTransformer(
                diamond_lattice,
                lambda: multiply_matrices(
                    translate((0, 0, 0)),
                    rotate((1, 0, 0), 0.13 * world.time()),
                    rotate((0, 0, 1), 0.11 * world.time()),
                    rotate((0, 1, 0), 0.07 * world.time())
                )
            ),
            lambda: world.get_variable("diamond_lattice_enabled")
        )
    )

    return scene


class UserInteractionHandler:

    def __init__(self, app, world):
        self._app = app
        self._world = world

    def process_keyboard_event(self, window, key: int, _scancode: int, action: int, mods: int):

        app = self._app
        world = self._world

        if action in (glfw.PRESS, glfw.REPEAT):
            match key:
                case glfw.KEY_SPACE:
                    freeze_status = world.get_freeze_status()
                    freeze_status = not freeze_status
                    world.set_freeze_status(freeze_status)
                case glfw.KEY_COMMA:
                    realtime_factor = world.get_realtime_factor()
                    realtime_factor = 0.5 * realtime_factor
                    world.set_realtime_factor(realtime_factor)
                case glfw.KEY_PERIOD:
                    realtime_factor = world.get_realtime_factor()
                    realtime_factor = 2.0 * realtime_factor
                    world.set_realtime_factor(realtime_factor)
                case glfw.KEY_SLASH:
                    realtime_factor = world.get_realtime_factor()
                    realtime_factor = -realtime_factor
                    world.set_realtime_factor(realtime_factor)
                case glfw.KEY_ESCAPE:
                    glfw.set_window_should_close(window, True)
                case glfw.KEY_0:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    diamond_lattice.cut_mode = 0
                case glfw.KEY_1:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    diamond_lattice.cut_mode = 1 if diamond_lattice.cut_mode != 1 else 0
                case glfw.KEY_2:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    diamond_lattice.cut_mode = 2 if diamond_lattice.cut_mode != 2 else 0
                case glfw.KEY_3:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    diamond_lattice.cut_mode = 3 if diamond_lattice.cut_mode != 3 else 0
                case glfw.KEY_C:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    diamond_lattice.color_mode = (diamond_lattice.color_mode + 1) % 3
                case glfw.KEY_D:
                    diamond_lattice_enabled = world.get_variable("diamond_lattice_enabled")
                    diamond_lattice_enabled = not diamond_lattice_enabled
                    world.set_variable("diamond_lattice_enabled", diamond_lattice_enabled)
                case glfw.KEY_F:
                    app.toggle_fullscreen(window)
                case glfw.KEY_L:
                    floor_enabled = world.get_variable("floor_enabled")
                    floor_enabled = not floor_enabled
                    world.set_variable("floor_enabled", floor_enabled)
                case glfw.KEY_I:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    diamond_lattice.impostor_mode = (diamond_lattice.impostor_mode + 1) % 2
                case glfw.KEY_RIGHT_BRACKET:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    if (mods & glfw.MOD_SHIFT) != 0:
                        diamond_lattice.unit_cells_per_dimension = diamond_lattice.unit_cells_per_dimension + 2
                    else:
                        diamond_lattice.crystal_side_length = diamond_lattice.crystal_side_length + 2.0
                case glfw.KEY_LEFT_BRACKET:
                    diamond_lattice = world.get_variable("diamond_lattice")
                    if (mods & glfw.MOD_SHIFT) != 0:
                        diamond_lattice.unit_cells_per_dimension = max(1, diamond_lattice.unit_cells_per_dimension - 2)
                    else:
                        diamond_lattice.crystal_side_length = max(0, diamond_lattice.crystal_side_length - 2.0)
                case glfw.KEY_UP:
                    render_distance = world.get_variable("render_distance")
                    render_distance = max(0.0, render_distance - 5.0)
                    world.set_variable("render_distance", render_distance)
                case glfw.KEY_DOWN:
                    render_distance = world.get_variable("render_distance")
                    render_distance = render_distance + 5.0
                    world.set_variable("render_distance", render_distance)

    def process_cursor_position_event(self, window, xpos: float, ypos: float):
        print("mouse position:", xpos, ypos)

    def process_mouse_button_event(self, window, button: int, action: int, mods: int):
        print("mouse button:", button, action, mods)

    def process_scroll_event(self, window, xoffset: float, yoffset: float):
        print("mouse scroll button:", xoffset, yoffset)


class Application:

    def __init__(self):
        self._user_interaction_handler = None
        self._window_position_and_size = None

    @staticmethod
    def create_glfw_window(version_major: int, version_minor: int):
        """Create a window using GLFW."""

        # Set up window creation hints.

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, version_major)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, version_minor)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        # Create the window.

        monitor = glfw.get_primary_monitor()
        current_mode = glfw.get_video_mode(monitor)

        width = 640
        height = 480
        window = glfw.create_window(width, height, "DiamondViewer", None, None)

        if not window:
            raise RuntimeError("Unable to create window using GLFW.")

        return window

    def toggle_fullscreen(self, window):
        monitor = glfw.get_window_monitor(window)
        if monitor:
            # The window is a fullscreen window on the given monitor.
            # Switch to non-fullscreen mode.
            # Note: the refresh rate is ignored when no monitor is specified.
            (xpos, ypos, width, height) = self._window_position_and_size
            glfw.set_window_monitor(window, None, xpos, ypos, width, height, 0)
        else:
            # The window is a regular window.
            # Make it a fullscreen window.
            monitor = glfw.get_primary_monitor()
            current_mode = glfw.get_video_mode(monitor)
            (xpos, ypos) = glfw.get_window_pos(window)
            (width, height) = glfw.get_window_size(window)
            self._window_position_and_size = (xpos, ypos, width, height)
            glfw.set_window_monitor(window, monitor, 0, 0, current_mode.size.width, current_mode.size.height, current_mode.refresh_rate)

    def run(self):

        """Main entry point."""

        if not glfw.init():
            raise RuntimeError("Unable to initialize GLFW.")

        # Create a GLFW window and set it as the current OpenGL context.

        window = Application.create_glfw_window(4, 1)

        # glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)

        glfw.set_framebuffer_size_callback(window, lambda *args: self.framebuffer_size_callback(*args))
        glfw.set_key_callback(window, lambda *args: self.key_callback(*args))
        glfw.set_cursor_pos_callback(window, lambda *args: self.cursor_position_callback(*args))
        glfw.set_mouse_button_callback(window, lambda *args: self.mouse_button_callback(*args))
        glfw.set_scroll_callback(window, lambda *args: self.scroll_callback(*args))

        glfw.make_context_current(window)

        world = World()

        world.set_variable("render_distance", 60.0)

        self._user_interaction_handler = UserInteractionHandler(self, world)

        scene = make_scene(world)

        # Prepare loop.

        frame_counter = 0
        t_previous_wallclock = None

        glfw.swap_interval(1)

        glPointSize(1)
        glClearColor(0.12, 0.12, 0.12, 1.0)
        glEnable(GL_DEPTH_TEST)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        fov_degrees = 30.0
        near_plane = 0.5
        far_plane = 1000.0

        num_report_frames = 100

        while not glfw.window_should_close(window):

            t_wallclock = glfw.get_time()
            if frame_counter % num_report_frames == 0:
                if t_previous_wallclock is not None:
                    frame_duration = (t_wallclock - t_previous_wallclock) / num_report_frames
                    print("@@ {:20.4f} ms per frame".format(frame_duration * 1000.0))
                t_previous_wallclock = t_wallclock

            # Sample world time.
            # All queries to world.time() up until the next sample_time() call will give the same time value.

            world.sample_time()

            # Make view matrix.

            render_distance = world.get_variable("render_distance")

            view_matrix = translate((0.0, 0.0, -render_distance)) @ rotate((0, 1, 0), world.time() * 0.0)

            # Make model matrix.

            model_matrix = np.identity(4)

            # Make perspective projection matrix.

            (framebuffer_width, framebuffer_height) = glfw.get_framebuffer_size(window)

            if framebuffer_width > 0 and framebuffer_height > 0:

                projection_matrix = perspective_projection(
                    framebuffer_width,
                    framebuffer_height,
                    fov_degrees,
                    near_plane,
                    far_plane
                )

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                scene.render(projection_matrix, view_matrix, model_matrix)

                glfw.swap_buffers(window)

            glfw.poll_events()
            frame_counter += 1

        scene.close()

        glfw.destroy_window(window)
        glfw.terminate()

    @staticmethod
    def framebuffer_size_callback(_window, width, height):
        print("Resizing framebuffer:", width, height)
        glViewport(0, 0, width, height)

    def key_callback(self, window, key: int, scancode: int, action: int, mods: int):
        if self._user_interaction_handler is not None:
            self._user_interaction_handler.process_keyboard_event(window, key, scancode, action, mods)

    def cursor_position_callback(self, window, xpos: float, ypos: float):
        if self._user_interaction_handler is not None:
            self._user_interaction_handler.process_cursor_position_event(window, xpos, ypos)

    def mouse_button_callback(self, window, button: int, action: int, mods: int):
        if self._user_interaction_handler is not None:
            self._user_interaction_handler.process_mouse_button_event(window, button, action, mods)

    def scroll_callback(self, window, xoffset: float, yoffset: float):
        if self._user_interaction_handler is not None:
            self._user_interaction_handler.process_scroll_event(window, xoffset, yoffset)


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

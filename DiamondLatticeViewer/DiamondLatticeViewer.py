#! /usr/bin/env python3

import numpy as np

import glfw
from OpenGL.GL import *

from utilities.matrices import translate, rotate, scale, perspective_projection

from renderables import (RenderablePlanet, RenderableFloor, RenderableScene, RenderableModelTransformer,
                         RenderableSphereImpostor, RenderableCylinderImpostor,
                         RenderableDiamondLattice)

from utilities.world import World


def make_scene(world: World) -> RenderableScene:
    """Create a scene in the world."""

    scene = RenderableScene()

    draw_floor = False
    if draw_floor:
        scene.add_model(
            RenderableModelTransformer(
                RenderableFloor(8.0, 8.0),
                lambda: translate((0, 0, 0))
            )
        )

    draw_earth = False
    if draw_earth:
        # add center earth with smaller earths around it.

        earth = RenderablePlanet()

        scene.add_model(
            RenderableModelTransformer(
                earth,
                lambda: translate((0, 0.0, 0)) @ scale(4.0) @ rotate((0, 1, 0), world.time())
            )
        )

    draw_sphere_impostor = False
    if draw_sphere_impostor:
        sphere_imposter_constellation = RenderableScene()

        earth = RenderableSphereImpostor("earth.png")

        sphere_imposter_constellation.add_model(
            RenderableModelTransformer(
                earth,
                lambda: translate((+0.8, 0.0, 0)) @ scale((1.0, 1.0, 1.0)) @ rotate((0, 1, 0), 0 * world.time())
            )
        )

        moon = RenderableSphereImpostor("moon.png")

        sphere_imposter_constellation.add_model(
            RenderableModelTransformer(
                moon,
                lambda: translate((-0.8, 0.0, 0.3)) @ scale((1.0, 1.0, 1.0)) @ rotate((0, 1, 0), 0 * world.time())
            )
        )

        scene.add_model(
            RenderableModelTransformer(
                sphere_imposter_constellation,
                lambda: rotate((0, 1, 0), 1 * world.time())
            )
        )

    draw_cylinder_impostor = False
    if draw_cylinder_impostor:
        cylinder_impostor = RenderableCylinderImpostor()

        scene.add_model(
            RenderableModelTransformer(
                cylinder_impostor,
                lambda: translate((+0.25, 0.0, 0)) @ rotate((0, 1, 0), 0 * world.time()) @ rotate((1, 0, 0),
                                                                                                  0.5 * world.time()) @ scale(
                    (0.2, 0.2, 4.0))
            )
        )

        sphere_impostor = RenderableSphereImpostor("earth.png")

        scene.add_model(
            RenderableModelTransformer(
                sphere_impostor,
                lambda: translate((+0.0, 0.0, 0)) @ scale((1.0, 1.0, 1.0)) @ rotate((0, 1, 0), 1 * world.time())
            )
        )

    draw_diamond_impostor = True
    if draw_diamond_impostor:
        diamond_lattice = RenderableDiamondLattice(name="diamond_lattice")

        scene.add_model(
            RenderableModelTransformer(
                diamond_lattice,
                lambda: translate((0, 0, 0)) @ rotate((1, 0, 0), 0.13 * world.time()) @ rotate((0, 0, 1), 0.11 * world.time()) @ rotate((0, 1, 0), 0.07 * world.time())
            )
        )

    return scene


class Application:

    def __init__(self):
        self.render_distance = 60.0
        self._diamond_model = None
        self._world = None

    @staticmethod
    def create_glfw_window(version_major: int, version_minor: int, fullscreen_flag: bool):
        """Create a window using GLFW."""

        # Set up window creation hints.

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, version_major)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, version_minor)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        # Create the window.

        use_secondary_monitor = False
        if use_secondary_monitor:
            monitors = glfw.get_monitors()
            monitor = monitors[-1]

            modes = glfw.get_video_modes(monitor)
            for mode in modes:
                print("mode:", mode.size, mode.bits, mode.refresh_rate)

            window = glfw.create_window(3840, 2160, "DiamondViewer", monitor, None)
        else:
            window = glfw.create_window(640, 480, "DiamondViewer", None, None)

        if not window:
            raise RuntimeError("Unable to create window using GLFW.")

        return window

    def run(self):

        """Main entry point."""

        if not glfw.init():
            raise RuntimeError("Unable to initialize GLFW.")

        # Create a GLFW window and set it as the current OpenGL context.

        window = Application.create_glfw_window(4, 1, True)

        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)

        glfw.set_framebuffer_size_callback(window, lambda *args: Application.framebuffer_size_callback(*args))
        glfw.set_key_callback(window, lambda *args: self.key_callback(*args))

        glfw.make_context_current(window)

        self._world = world = World()

        scene = make_scene(self._world)

        self._diamond_model = scene.find("diamond_lattice")

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

            # Sample world time. All queries to world.time() will be identical.
            world.sample_time()

            # Make view matrix.

            m_view = translate((0.0, 0, -self.render_distance)) @ rotate((0, 1, 0), world.time() * 0.0)

            # Make model matrix.

            m_model = np.identity(4)

            # Make perspective projection matrix.

            (framebuffer_width, framebuffer_height) = glfw.get_framebuffer_size(window)

            if framebuffer_width * framebuffer_height == 0:
                continue

            m_projection = perspective_projection(framebuffer_width, framebuffer_height, fov_degrees, near_plane, far_plane)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            scene.render(m_projection, m_view, m_model)

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

    def key_callback(self, window, key: int, _scancode: int, action: int, mods: int):

        if action in (glfw.PRESS, glfw.REPEAT):
            match key:
                case glfw.KEY_SPACE:
                    rtf = self._world.get_realtime_factor()
                    rtf = 1.0 if rtf == 0.0 else 0.0
                    self._world.set_realtime_factor(rtf)
                case glfw.KEY_COMMA:
                    rtf = self._world.get_realtime_factor()
                    rtf = 0.5 * rtf
                    self._world.set_realtime_factor(rtf)
                case glfw.KEY_PERIOD:
                    rtf = self._world.get_realtime_factor()
                    rtf = 2.0 * rtf
                    self._world.set_realtime_factor(rtf)
                case glfw.KEY_SLASH:
                    rtf = self._world.get_realtime_factor()
                    rtf = -rtf
                    self._world.set_realtime_factor(rtf)
                case glfw.KEY_ESCAPE:
                    glfw.set_window_should_close(window, True)
                case glfw.KEY_0:
                    if self._diamond_model is not None:
                        self._diamond_model.cut_mode = 0
                case glfw.KEY_1:
                    if self._diamond_model is not None:
                        self._diamond_model.cut_mode = 1 if self._diamond_model.cut_mode != 1 else 0
                case glfw.KEY_2:
                    if self._diamond_model is not None:
                       self._diamond_model.cut_mode = 2 if self._diamond_model.cut_mode != 2 else 0
                case glfw.KEY_3:
                    if self._diamond_model is not None:
                        self._diamond_model.cut_mode = 3 if self._diamond_model.cut_mode != 3 else 0
                case glfw.KEY_C:
                    if self._diamond_model is not None:
                        self._diamond_model.color_mode = (self._diamond_model.color_mode + 1) % 2
                case glfw.KEY_I:
                    if self._diamond_model is not None:
                        self._diamond_model.impostor_mode = (self._diamond_model.impostor_mode + 1) % 2
                case glfw.KEY_RIGHT_BRACKET:
                    if self._diamond_model is not None:
                        if (mods & glfw.MOD_SHIFT) != 0:
                            self._diamond_model.unit_cells_per_dimension = self._diamond_model.unit_cells_per_dimension + 2
                        else:
                            self._diamond_model.crystal_side_length = self._diamond_model.crystal_side_length + 2.0
                case glfw.KEY_LEFT_BRACKET:
                        if self._diamond_model is not None:
                            if (mods & glfw.MOD_SHIFT) != 0:
                                self._diamond_model.unit_cells_per_dimension = max(1, self._diamond_model.unit_cells_per_dimension - 2)
                            else:
                                self._diamond_model.crystal_side_length = max(0, self._diamond_model.crystal_side_length - 2.0)
                case glfw.KEY_UP:
                    self.render_distance = max(0.0, self.render_distance - 5.0)
                case glfw.KEY_DOWN:
                        self.render_distance = self.render_distance + 5.0

            if self._diamond_model is not None:
                print("render distance {} diamond cut: {} diamond unit_cells_per_dimension: {} diamond crystal_side_length: {}".format(
                    self.render_distance,
                    self._diamond_model.cut_mode,
                    self._diamond_model.unit_cells_per_dimension,
                    self._diamond_model.crystal_side_length
                ))


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

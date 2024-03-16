"""This module implements the World class."""

from typing import Any

import glfw


class World:

    def __init__(self):
        self._sample_time = glfw.get_time()
        self._alpha = 0.0
        self._beta = 1.0
        self._freeze_time = None  # None if not frozen.
        self._variables = {}

    def sample_time(self):
        self._sample_time = glfw.get_time()

    def time(self):
        if self._freeze_time is not None:
            return self._freeze_time
        return self._alpha + self._beta * self._sample_time

    def set_realtime_factor(self, realtime_factor: float):
        t = glfw.get_time()
        # self._alpha + self._beta * t == new_alpha + rtf * t
        # new_alpha == self._alpha + (self._beta - rtf) * t
        self._alpha += (self._beta - realtime_factor) * t
        self._beta = realtime_factor

    def get_realtime_factor(self):
        return self._beta

    def set_freeze_status(self, freeze_status: bool):
        if freeze_status:
            # We're being asked to freeze time.
            if self._freeze_time is None:
                self._freeze_time = self.time()
        else:
            # We're being asked to unfreeze time.
            if self._freeze_time is not None:
                t = glfw.get_time()
                # freeze_time == new_alpha + self._beta * t
                # new_alpha = freeze_time - self._beta * t
                self._alpha = self._freeze_time - self._beta * t
                self._freeze_time = None

    def get_freeze_status(self) -> bool:
        return self._freeze_time is not None

    def set_variable(self, name: str, value: Any):
        print("Setting variable {!r} to value {}.".format(name, value))
        self._variables[name] = value

    def get_variable(self, name):
        return self._variables.get(name)

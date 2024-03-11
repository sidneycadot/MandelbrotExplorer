"""This module implements the World class."""


from typing import Any

import glfw


class World:

    def __init__(self):
        self._sample_time = glfw.get_time()
        self._alpha = 0.0
        self._beta = 1.0
        self._variables = {}

    def sample_time(self):
        self._sample_time = glfw.get_time()
        return self.time()

    def time(self):
        return self._alpha + self._beta * self._sample_time

    def set_realtime_factor(self, realtime_factor: float):
        t = glfw.get_time()
        # self._alpha + self._beta * t == new_alpha + rtf * t
        # new_alpha == self._alpha + (self._beta - rtf) * t
        self._alpha += (self._beta - realtime_factor) * t
        self._beta = realtime_factor

    def get_realtime_factor(self):
        return self._beta

    def set_variable(self, name: str, value: Any):
        print("@@ setting variable {!r} to value {}.".format(name, value))
        self._variables[name] = value

    def get_variable(self, name):
        return self._variables[name]

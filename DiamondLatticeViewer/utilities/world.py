
import glfw


class World:

    def __init__(self):
        self._sample_time = glfw.get_time()
        self._alpha = 0.0
        self._beta = 1.0

    def sample_time(self):
        self._sample_time = glfw.get_time()
        return self.time()

    def time(self):
        return self._alpha + self._beta * self._sample_time

    def set_realtime_factor(self, rtf: float):
        t = glfw.get_time()
        # self._alpha + self._beta * t == new_alpha + rtf * t
        # new_alpha == self._alpha + (self._beta - rtf) * t
        self._alpha += (self._beta - rtf) * t
        self._beta = rtf

    def get_realtime_factor(self):
        return self._beta

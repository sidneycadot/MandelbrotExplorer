class World:

    def __init__(self):
        self._time = 0.0

    def set_time(self, time: float):
        self._time = time

    def time(self):
        return self._time

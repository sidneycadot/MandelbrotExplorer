"""Provide the Renderable abstract base class."""


class Renderable:
    def render(self, projection_matrix, view_matrix, model_matrix):
        raise NotImplementedError()

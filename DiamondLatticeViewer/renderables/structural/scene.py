"""This module implements the RenderableScene class."""

from ..renderable import Renderable


class RenderableScene(Renderable):
    """A collection of renderable objects."""

    def __init__(self):
        self._models = []

    def close(self) -> None:
        for model in self._models:
            model.close()

    def add_model(self, model: Renderable) -> None:
        self._models.append(model)

    def render(self, projection_matrix, model_matrix, view_matrix) -> None:
        for model in self._models:
            model.render(projection_matrix, model_matrix, view_matrix)

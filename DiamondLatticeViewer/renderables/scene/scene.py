"""This module implements the RenderableScene class."""

from typing import Optional

from renderables.renderable import Renderable


class RenderableScene(Renderable):
    """A collection of renderable models."""
    def __init__(self, name: Optional[str] = None):

        super().__init__(name)
        self._models = []

    def close(self) -> None:
        for model in self._models:
            model.close()
        self._models.clear()

    def add_model(self, model: Renderable):
        self._models.append(model)

    def render(self, m_projection, m_view, m_model) -> None:
        for model in self._models:
            model.render(m_projection, m_view, m_model)

    def children(self):
        # Return a copy, to prevent accidental modification.
        return list(self._models)

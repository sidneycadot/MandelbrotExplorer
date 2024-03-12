"""This module implements the RenderableModelTransformer class."""

from ..renderable import Renderable


class RenderableOptionalModel(Renderable):
    """A renderable wrapper that dynamically decides if the wrapped object should be rendered."""

    def __init__(self, model, func):

        self._model = model
        self._func = func

    def close(self) -> None:
        self._model.close()
        self._model = None
        self._func = None

    def render(self, m_projection, m_view, m_model) -> None:
        if self._func():
            self._model.render(m_projection, m_view, m_model)

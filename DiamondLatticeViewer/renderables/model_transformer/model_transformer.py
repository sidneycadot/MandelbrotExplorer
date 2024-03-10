"""This module implements the RenderableModelTransformer class."""

from typing import Optional

from renderables.renderable import Renderable


class RenderableModelTransformer(Renderable):

    def __init__(self, model, func, name: Optional[str] = None):

        super().__init__(name)

        self._model = model
        self._func = func

    def close(self):
        self._model.close()
        self._model = None
        self._func = None

    def render(self, m_projection, m_view, m_model):
        m_func = self._func()
        self._model.render(m_projection, m_view, m_model @ m_func)

    def children(self):
        return [self._model]

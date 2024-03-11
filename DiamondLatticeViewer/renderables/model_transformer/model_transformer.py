"""This module implements the RenderableModelTransformer class."""

from typing import Optional

from renderables.renderable import Renderable


class RenderableModelTransformer(Renderable):

    def __init__(self, model, func):

        self._model = model
        self._func = func

    def close(self):
        self._model.close()
        self._model = None
        self._func = None

    def render(self, projection_matrix, view_matrix, model_matrix):
        m_func = self._func()
        self._model.render(projection_matrix, view_matrix, model_matrix @ m_func)


from renderables.renderable import Renderable


class RenderableTransformer(Renderable):

    def __init__(self, model, func):
        self._model = model
        self._func = func

    def render(self, m_xform):
        m_func = self._func()
        self._model.render(m_xform @ m_func)

"""Provide the Renderable abstract base class."""


class Renderable:
    def render(self, m_projection, m_view, m_model):
        raise NotImplementedError()

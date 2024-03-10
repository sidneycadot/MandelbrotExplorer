"""Provide the Renderable abstract base class."""

from typing import Optional


class Renderable:
    """Base class for Renderables."""

    def __init__(self, name: Optional[str]):
        self.name = name

    def render(self, projection_matrix, view_matrix, model_matrix):
        raise NotImplementedError()

    def children(self):
        """Generate all direct children.

        Most Renderable objects have no descendants, which is why that is the default implementation.
        Renderable objects that have children should override this method.
        """
        yield from ()

    def all_nodes(self):
        yield self
        for child in self.children():
            yield from child.all_nodes()

    def find(self, name: str):
        candidates = [node for node in self.all_nodes() if node.name == name]
        match len(candidates):
            case 0: return None
            case 1: return candidates[0]
            case _: raise RuntimeError("Multiple matches for name {!r}.".format(name))

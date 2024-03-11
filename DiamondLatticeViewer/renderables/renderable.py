"""Provide the Renderable abstract base class for renderable objects."""

from typing import Optional


class Renderable:
    """Abstract base class for renderable objects."""

    def __init__(self, name: Optional[str]):
        self.name = name

    def render(self, projection_matrix, view_matrix, model_matrix):
        """Must be implemented by derived classes."""
        raise NotImplementedError()

    def children(self):
        """Generate all direct children.

        Most Renderable objects have no descendants, which is why that is the default implementation.
        Renderable objects that have children should override this method.
        """
        yield from ()

    def all_nodes(self):
        """A generator that yields all nodes, including self."""
        yield self
        for child in self.children():
            yield from child.all_nodes()

    def find(self, name: str):
        candidates = [node for node in self.all_nodes() if node.name == name]
        match len(candidates):
            case 0: return None
            case 1: return candidates[0]
            case _: raise RuntimeError("Multiple Renderable objects match name {!r}.".format(name))

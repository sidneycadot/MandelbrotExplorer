"""Provide the Renderable abstract base class."""

from typing import Optional


class Renderable:
    """Base class for Renderables."""

    def __init__(self, name: Optional[str]):
        self.name = name

    def render(self, projection_matrix, view_matrix, model_matrix):
        raise NotImplementedError()

    def children(self):
        """Get list of direct descendants.

        For most Renderable instances this list will be empty, which is why that is the default implementation.
        Renderables with children should override this method.
        """
        return []

    def all_nodes(self):
        nodes = [self]
        for child in self.children():
            nodes.extend(child.all_nodes())
        return nodes

    def find(self, name: str):
        nodes = self.all_nodes()
        print("FOUND", len(nodes), "nodes.")
        for node in nodes:
            if node.name is not None:
                print("NAMED NODE:", node.name)
        candidates = [node for node in nodes if node.name == name]
        match len(candidates):
            case 0: return None
            case 1: return candidates[0]
            case _: raise RuntimeError("Multiple matches.")

"""Provide the Renderable abstract base class for renderable objects."""

from typing import Optional


class Renderable:
    """Abstract base class for renderable objects."""

    def render(self, projection_matrix, view_matrix, model_matrix):
        """Must be implemented by derived classes."""
        raise NotImplementedError()

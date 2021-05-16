from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["Scene"]


class Scene(ABC):
    """
    Handles Scene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: UI

    def update(self):
        pass

    def render(self):
        pass


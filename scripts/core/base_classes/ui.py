from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.core.game import Game
    import pygame


__all__ = ["UI"]


class UI(ABC):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game):
        self.game: Game = game

    def update(self):
        pass

    def render(self, surface: pygame.surface):
        pass

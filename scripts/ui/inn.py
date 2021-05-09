from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from scripts.management.game import Game


__all__ = ["InnUI"]


class InnUI:
    """
    Represent the UI of the Inn screen.
    """

    def __init__(self, game: Game):
        self.game: Game = game

    def update(self):
        pass

    def render(self, surface: pygame.surface):
        pass

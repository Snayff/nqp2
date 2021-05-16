from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["InnUI"]


class InnUI(UI):
    """
    Represent the UI of the InnScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

    def update(self):
        pass

    def render(self, surface: pygame.surface):
        pass

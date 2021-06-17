from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from scripts.core.game import Game


__all__ = ["UI"]

#### To Do List######
# TODO - add an overlay method to draw standardised info such as gold
# TODO - add option selection and looping selection to update
# TODO - amend selection approach to work on a grid, so we can move across columns and rows.


class UI(ABC):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.default_font = self.game.assets.fonts["default"]
        self.disabled_font = self.game.assets.fonts["disabled"]
        self.warning_font = self.game.assets.fonts["warning"]
        self.positive_font = self.game.assets.fonts["positive"]

    def update(self):
        pass

    def render(self, surface: pygame.surface):
        pass

    def draw_gold(self, surface: pygame.surface):
        self.default_font.render(f"Gold: {self.game.memory.gold}", surface, (1, 1), 2)

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scripts.ui_elements.text import Font

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

        self.default_font: Font = self.game.assets.fonts["default"]
        self.disabled_font: Font = self.game.assets.fonts["disabled"]
        self.warning_font: Font = self.game.assets.fonts["warning"]
        self.positive_font: Font = self.game.assets.fonts["positive"]

        self.selected_index: int = 0  # for selecting options

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, surface: pygame.surface):
        pass

    def handle_selected_index_looping(self, max_index: int):
        """
        Manage the looping of the selection index
        """
        if self.selected_index < 0:
            self.selected_index = max_index - 1
        elif self.selected_index >= max_index:
            self.selected_index = 0

    def draw_gold(self, surface: pygame.surface):
        self.default_font.render(f"Gold: {self.game.memory.gold}", surface, (1, 1), 2)

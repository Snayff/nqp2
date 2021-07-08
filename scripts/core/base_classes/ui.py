from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    import pygame

    from scripts.core.game import Game


__all__ = ["UI"]


######### TO DO LIST ###############


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
        self.instruction_font: Font = self.game.assets.fonts["instruction"]

        self.selected_row: int = 0
        self.selected_col: int = 0
        self.max_rows: int = 0
        self.max_cols: int = 0
        self.last_row: int = 0

        self.temporary_instruction_text: str = ""
        self.temporary_instruction_timer: float = 0.0
        self.instruction_text: str = ""

    def update(self, delta_time: float):
        self.temporary_instruction_timer -= delta_time

        if self.temporary_instruction_timer <= 0:
            self.temporary_instruction_text = ""

    @abstractmethod
    def render(self, surface: pygame.surface):
        pass

    def set_selection_dimensions(self, max_rows: int, max_cols: int):
        self.max_rows = max_rows
        self.max_cols = max_cols

        # ensure we're on a valid column
        if self.selected_col >= max_cols:
            self.selected_col = max_cols

        # ensure we're on a valid row
        if self.selected_row >= max_rows:
            self.selected_row = max_rows

        self.last_row = max_rows - 1

    def set_instruction_text(self, text: str, temporary: bool = False):
        if temporary:
            self.temporary_instruction_text = text
            self.temporary_instruction_timer = 2
        else:
            self.instruction_text = text

    def handle_selector_index_looping(self):
        """
        Manage the looping of the selection index
        """
        # row
        if self.selected_row < 0:
            self.selected_row = self.max_rows - 1
        elif self.selected_row >= self.max_rows:
            self.selected_row = 0

        # col
        if self.selected_col < 0:
            self.selected_col = self.max_cols - 1
        elif self.selected_col >= self.max_cols:
            self.selected_col = 0

    def handle_directional_input_for_selection(self):
        """
        Handle amending the selected row and column with input
        """
        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_row -= 1

        if self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_row += 1

        if self.game.input.states["left"]:
            self.game.input.states["left"] = False
            self.selected_col -= 1

        if self.game.input.states["right"]:
            self.game.input.states["right"] = False
            self.selected_col += 1

    def draw_gold(self, surface: pygame.surface):
        self.disabled_font.render(f"Gold: {self.game.memory.gold}", surface, (2, 2))

    def draw_charisma(self, surface: pygame.surface):
        self.disabled_font.render(f"Charisma: {self.game.memory.commander.charisma_remaining}", surface, (62, 2))

    def draw_leadership(self, surface: pygame.surface):
        self.disabled_font.render(f"Leadership: {self.game.memory.commander.leadership}", surface, (122, 2))

    def draw_instruction(self, surface: pygame.surface):
        if self.temporary_instruction_text:
            text = self.temporary_instruction_text
            font = self.warning_font
        else:
            text = self.instruction_text
            font = self.instruction_font

        x = self.game.window.width - font.width(text) - 2
        y = 2
        font.render(text, surface, (x, y))

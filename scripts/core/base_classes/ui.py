from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from scripts.core.game import Game
    from typing import List, Optional, Dict, Type, Union
    from scripts.ui_elements.panel import Panel
    from scripts.ui_elements.font import Font
    from scripts.ui_elements.frame import Frame
    from scripts.ui_elements.unit_stats_frame import UnitStatsFrame


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

        self.elements: Dict[str, Union[Frame, UnitStatsFrame]] = {}
        self.panels: Dict[str, Panel] = {}
        self.current_panel: Optional[Panel] = None

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


    def rebuild_ui(self):
        self.elements = {}
        self.panels = {}


    def refresh_info(self):
        pass

    def set_instruction_text(self, text: str, temporary: bool = False):
        if temporary:
            self.temporary_instruction_text = text
            self.temporary_instruction_timer = 2
        else:
            self.instruction_text = text

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

    def draw_elements(self, surface: pygame.surface):
        for element in self.elements.values():
            element.render(surface)

    def add_panel(self, panel: Panel, name: str):
        """
        Adds panel to the panel dict. If it is the first panel then also sets it to the current panel and selects the
         first element.
        """
        self.panels[name] = panel

        if len(self.panels) == 1:
            self.current_panel = self.panels[name]
            self.current_panel.select_first_element()

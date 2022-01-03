from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI
from scripts.core.constants import FontType
import pygame

from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union
    from scripts.core.game import Game
    from scripts.core.base_classes.scene import Scene

__all__ = ["TestUI"]


######### TO DO LIST ###############


class TestUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, parent_scene: Scene):
        super().__init__(game, parent_scene, True)


    def update(self, delta_time: float):
        super().update(delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        create_font = self.game.assets.create_font

        stat_icon = self.game.assets.unit_animations["air_elemental"]["icon"][0]
        frame = Frame(
            (10, 10), image=stat_icon, font=create_font(FontType.DEFAULT, "text"), is_selectable=False
        )
        self.elements["test_ele"] = frame
        self.panels["test"] = Panel([frame], True)
        self.current_panel = self.panels["test"]
        self.current_panel.select_first_element()

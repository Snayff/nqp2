from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import FontType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game
    from scripts.scenes.test.scene import TestScene

__all__ = ["TestUI"]


######### TO DO LIST ###############


class TestUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, parent_scene: TestScene):
        super().__init__(game, False)
        self.parent_scene: TestScene = parent_scene

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
        frame = Frame((100, 10), image=stat_icon, font=create_font(FontType.DEFAULT, "test"), is_selectable=False)
        self.elements["test_ele"] = frame
        self.add_panel(Panel([frame], True), "test")

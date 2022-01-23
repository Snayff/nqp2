from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.ui_elements.unit_stats_frame import UnitStatsFrame

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game
    from scripts.scenes.view_troupe.scene import ViewTroupeScene

__all__ = ["ViewTroupeUI"]


class ViewTroupeUI(UI):
    """
    Represent the UI of the ViewTroupeScene.
    """

    def __init__(self, game: Game, parent_scene: ViewTroupeScene):
        super().__init__(game, True)
        self._parent_scene: ViewTroupeScene = parent_scene

        self.set_instruction_text(f"Press X to exit the troupe overview.")

    def update(self, delta_time: float):
        super().update(delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # generic input
        if self._game.input.states["down"]:
            self._game.input.states["down"] = False

            self._current_panel.select_next_element()

        if self._game.input.states["up"]:
            self._game.input.states["up"] = False

            self._current_panel.select_previous_element()

        if self._game.input.states["cancel"]:
            self._game.input.states["cancel"] = False

            # return to previous scene
            self._game.change_scene(self._game.troupe.previous_scene_type)

    def draw(self, surface: pygame.surface):
        # show core info
        self._draw_instruction(surface)

        # draw elements
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        units = self._game.memory.player_troupe.units

        # positions
        start_x = 20
        start_y = 40

        # draw options
        current_x = start_x
        current_y = start_y
        for count, unit in enumerate(units.values()):

            frame = UnitStatsFrame(self._game, (current_x, current_y), unit, False)
            self._elements[f"{unit.id}"] = frame
            # if we need to refer back to this we will need to change key

            current_x += 70

        self.rebuild_resource_elements()

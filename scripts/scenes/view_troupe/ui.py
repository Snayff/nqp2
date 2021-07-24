from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.unit_stats_frame import UnitStatsFrame

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["ViewTroupeUI"]


class ViewTroupeUI(UI):
    """
    Represent the UI of the ViewTroupeScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.set_instruction_text(f"Press X to exit the troupe overview.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # generic input
        if self.game.input.states["down"]:
            self.game.input.states["down"] = False

            self.current_panel.select_next_element()

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False

            self.current_panel.select_previous_element()

        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to previous scene
            self.game.change_scene(self.game.troupe.previous_scene_type)

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        units = self.game.memory.player_troupe.units

        # positions
        start_x = 20
        start_y = 40

        # draw options
        current_x = start_x
        current_y = start_y
        for count, unit in enumerate(units.values()):

            frame = UnitStatsFrame(self.game, (current_x, current_y), unit, False)
            self.elements[f"{unit.id}"] = frame
            # if we need to refer back to this we will need to change key

            current_x += 70

        self.rebuild_resource_elements()

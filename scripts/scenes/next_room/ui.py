from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, EventState, FontEffects, FontType, GAP_SIZE, SceneType
from scripts.core.debug import Timer
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from scripts.core.game import Game
    from scripts.scenes.next_room.scene import NextRoomScene


__all__ = ["NextRoomUI"]


class NextRoomUI(UI):
    """
    Represent the UI of the NextRoomScene.

    """

    def __init__(self, game: Game, parent_scene: NextRoomScene):
        with Timer("EventScene initialisation"):
            super().__init__(game, True)
            self.parent_scene: NextRoomScene = parent_scene
            self.selected_option: str = ""
            self.set_instruction_text("Choose where to go.")

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # selection in panel
        if self._game.input.states["down"]:
            self._game.input.states["down"] = False
            self._current_panel.select_next_element()
        if self._game.input.states["up"]:
            self._game.input.states["up"] = False
            self._current_panel.select_previous_element()

        if self._game.input.states["select"]:
            self._game.input.states["select"] = False
            self._game.world.controller.move_to_new_room()
            self._game.deactivate_scene(SceneType.NEXT_ROOM)

    def draw(self, surface: pygame.Surface):
        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        # positions
        start_x = 18
        start_y = 50

        # values needed for multiple elements
        window_width = self._game.window.width
        window_height = self._game.window.height
        create_font = self._game.assets.create_font
        frame_line_width = window_width - (start_x * 2)

        # draw background
        bg_surface = pygame.Surface((frame_line_width, window_height - (start_y * 2)), SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        frame = Frame((start_x, start_y), image=bg_surface, is_selectable=False)
        self.elements[f"background"] = frame

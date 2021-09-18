from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, GameState, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["MainMenuUI"]


class MainMenuUI(UI):
    """
    Represent the UI of the MainMenuScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

    def update(self, delta_time: float):
        super().update(delta_time)

        self.update_elements(delta_time)

        # generic input
        if self.game.input.states["down"]:
            self.game.input.states["down"] = False

            self.current_panel.select_next_element()

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False

            self.current_panel.select_previous_element()

        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            selected_element = self.current_panel.selected_element
            if selected_element == self.elements["new_game"]:
                self.game.main_menu.new_game()

            elif selected_element == self.elements["exit"]:
                self.game.state = GameState.EXITING

    def render(self, surface: pygame.surface):
        # N.B. dont draw instruction
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        create_font = self.game.assets.create_font
        window_width = self.game.window.width
        window_height = self.game.window.height

        # positions
        start_x = 10
        start_y = window_height - 100

        # draw background
        background = self.game.assets.get_image("ui", "town", (window_width, window_height))
        frame = Frame((0, 0), background)
        self.elements["background"] = frame

        # draw options
        current_x = start_x
        current_y = start_y
        panel_elements = []

        # new game
        frame = Frame((current_x, current_y), font=create_font(FontType.DEFAULT, "New Game"), is_selectable=True)
        self.elements["new_game"] = frame
        panel_elements.append(frame)

        # load
        current_y += frame.height + GAP_SIZE
        frame = Frame((current_x, current_y), font=create_font(FontType.DEFAULT, "Load Game"), is_selectable=False)
        self.elements["load_game"] = frame
        panel_elements.append(frame)

        # options
        current_y += frame.height + GAP_SIZE
        frame = Frame((current_x, current_y), font=create_font(FontType.DEFAULT, "Settings"), is_selectable=False)
        self.elements["settings"] = frame
        panel_elements.append(frame)

        # exit
        current_y += frame.height + GAP_SIZE
        frame = Frame((current_x, current_y), font=create_font(FontType.DEFAULT, "Exit"), is_selectable=True)
        self.elements["exit"] = frame
        panel_elements.append(frame)

        # add panel
        panel = Panel(panel_elements, True)
        self.add_panel(panel, "options")

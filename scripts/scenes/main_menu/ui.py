from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import FontType, GameState, GAP_SIZE
from scripts.ui_elements.generic.ui_frame import UIFrame
from scripts.ui_elements.generic.ui_panel import UIPanel

if TYPE_CHECKING:
    from scripts.core.game import Game
    from scripts.scenes.main_menu.scene import MainMenuScene


__all__ = ["MainMenuUI"]


class MainMenuUI(UI):
    """
    Represent the UI of the MainMenuScene.
    """

    def __init__(self, game: Game, parent_scene: MainMenuScene):
        super().__init__(game, True)
        self._parent_scene: MainMenuScene = parent_scene

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

        if self._game.input.states["select"]:
            self._game.input.states["select"] = False

            selected_element = self._current_panel.selected_element
            if selected_element == self._elements["new_game"]:
                self._parent_scene._new_game()

            elif selected_element == self._elements["exit"]:
                self._game.state = GameState.EXITING

    def draw(self, surface: pygame.Surface):
        # N.B. dont draw instruction
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        create_font = self._game.assets.create_font
        window_width = self._game.window.width
        window_height = self._game.window.height

        # positions
        start_x = 50
        start_y = window_height - 100

        # draw background
        background = self._game.assets.get_image("ui", "town", (window_width, window_height))
        frame = UIFrame(self._game, (0, 0), background)
        self._elements["background"] = frame

        # draw options
        current_x = start_x
        current_y = start_y
        panel_elements = []

        # new game
        frame = UIFrame(
            self._game, (current_x, current_y), font=create_font(FontType.DEFAULT, "New Game"), is_selectable=True
        )
        self._elements["new_game"] = frame
        panel_elements.append(frame)

        # load
        current_y += frame.height + GAP_SIZE
        frame = UIFrame(
            self._game, (current_x, current_y), font=create_font(FontType.DEFAULT, "Load Game"), is_selectable=False
        )
        self._elements["load_game"] = frame
        panel_elements.append(frame)

        # options
        current_y += frame.height + GAP_SIZE
        frame = UIFrame(
            self._game, (current_x, current_y), font=create_font(FontType.DEFAULT, "Settings"), is_selectable=False
        )
        self._elements["settings"] = frame
        panel_elements.append(frame)

        # exit
        current_y += frame.height + GAP_SIZE
        frame = UIFrame(
            self._game, (current_x, current_y), font=create_font(FontType.DEFAULT, "Exit"), is_selectable=True
        )
        self._elements["exit"] = frame
        panel_elements.append(frame)

        # add panel
        panel = UIPanel(self._game, panel_elements, True)
        self.add_panel(panel, "options")

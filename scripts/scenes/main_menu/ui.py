from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GameState, GAP_SIZE, SceneType
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

        self.fancy_font = None

    def update(self, delta_time: float):
        super().update(delta_time)

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

        if self.fancy_font is not None:
            self.fancy_font.update(delta_time)

    def render(self, surface: pygame.surface):
        # N.B. dont draw instruction

        #self.draw_elements(surface)

        self.fancy_font.render(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        default_font = self.default_font

        # positions
        window_width = self.game.window.width
        window_height = self.game.window.height
        start_x = 10
        start_y = window_height - 100
        font_height = default_font.height

        # draw background
        background = self.game.assets.get_image("ui", "town", (window_width, window_height))
        frame = Frame((0, 0), background)
        self.elements["background"] = frame

        # draw options
        current_x = start_x
        current_y = start_y
        panel_elements = []

        # new game
        frame = Frame((current_x, current_y), text_and_font=("New Game", default_font), is_selectable=True)
        self.elements["new_game"] = frame
        panel_elements.append(frame)

        # load
        current_y += font_height + GAP_SIZE
        frame = Frame((current_x, current_y), text_and_font=("Load Game", default_font), is_selectable=False)
        self.elements["load_game"] = frame
        panel_elements.append(frame)

        # options
        current_y += font_height + GAP_SIZE
        frame = Frame((current_x, current_y), text_and_font=("settings", default_font), is_selectable=False)
        self.elements["settings"] = frame
        panel_elements.append(frame)

        # exit
        current_y += font_height + GAP_SIZE
        frame = Frame((current_x, current_y), text_and_font=("Exit", default_font), is_selectable=True)
        self.elements["exit"] = frame
        panel_elements.append(frame)

        # add panel
        panel = Panel(panel_elements, True)
        self.add_panel(panel, "options")

        # TEST
        from scripts.ui_elements.fancy_font import FancyFont
        from scripts.ui_elements.font import Font
        my_font = Font('assets/fonts/small_font.png', (255, 255, 255))
        my_big_font = Font('assets/fonts/large_font.png', (255, 255, 255))
        my_red_font = Font('assets/fonts/small_font.png', (255, 0, 0))
        my_str = 'abcdef<!1>gh<!0>i<!1>j<!0>klmnop qrstuvwxyz<!2>ABCDEF Hello W<!0>orld!\n\nbapjs odhao<!1>ishdoi ahoidhaoin aisdiahs asdio<!0>haph adsiahspahd aisohdoiahd\n\ndhaihdaiuhdw adhoaihdhaioiohasdiaoh'
        my_str += '\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. <!1>Ut enim<!0> ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        font = FancyFont(my_str, my_font, my_red_font, my_big_font, max_width=200)
        self.fancy_font =font

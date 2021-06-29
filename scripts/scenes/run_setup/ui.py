from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["RunSetupUI"]


class RunSetupUI(UI):
    """
    Represent the UI of the RunSetupScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        num_homes = len(self.game.data.homes)
        self.dimensions: Dict[int, int] = {0: num_homes, 1: num_homes, 2: 1, 3: 1}

    def update(self):

        self.handle_selection_dimensions(len(self.dimensions.keys()), self.dimensions[self.selected_row])
        self.handle_directional_input_for_selection()
        self.handle_selected_index_looping()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            self.handle_selection()

        if self.game.input.states["toggle_data_editor"]:
            self.game.input.states["toggle_data_editor"] = False

            self.game.change_scene(SceneType.DEV_UNIT_DATA)

    def render(self, surface: pygame.surface):
        default_font = self.default_font
        positive_font = self.positive_font
        disabled_font = self.disabled_font

        homes = self.game.data.homes
        num_sections = 4  # home, ally, seed, confirm
        current_row = 0

        # positions
        start_x = 20
        start_y = 20
        gap = 10
        font_height = 12  # FIXME - get actual font height
        section_width = (self.game.window.width - (start_x * 2)) // len(homes)
        section_height = (self.game.window.height - (start_y * 2)) // num_sections

        # draw home options
        count = 0
        current_y = start_y
        for home in homes:
            current_x = start_x + (count * (section_width + gap))

            # get correct font
            if self.game.run_setup.selected_home == home:
                # selected already
                active_font = positive_font
            elif self.game.run_setup.selected_ally == home:
                # already used by other option
                active_font = disabled_font
            else:
                active_font = default_font

            active_font.render(home, surface, (current_x, current_y))

            # draw selector
            if count == self.selected_col and current_row == self.selected_row:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (current_x, current_y + font_height),
                    (current_x + default_font.width("home"), current_y + font_height),
                )

            count += 1

        # increment
        current_y += section_height
        current_row += 1

        # draw ally options
        count = 0
        for home in homes:
            current_x = start_x + (count * (section_width + gap))

            # get correct font
            if self.game.run_setup.selected_ally == home:
                # selected already
                active_font = positive_font
            elif self.game.run_setup.selected_home == home:
                # already used by other option
                active_font = disabled_font
            else:
                active_font = default_font

            active_font.render(home, surface, (current_x, current_y))

            # draw selector
            if count == self.selected_col and current_row == self.selected_row:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (current_x, current_y + font_height),
                    (current_x + default_font.width("home"), current_y + font_height),
                )

            count += 1

        # increment
        current_y += section_height
        current_row += 1

        # draw seed
        current_x = start_x
        count = 0

        active_font = default_font
        active_font.render("Seed: " + str(self.game.run_setup.selected_seed), surface, (current_x, current_y))

        # draw selector
        if count == self.selected_col and current_row == self.selected_row:
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (current_x, current_y + font_height),
                (current_x + default_font.width("home"), current_y + font_height),
            )

        # increment
        current_y += section_height
        current_row += 1

        # draw confirm option
        current_x = start_x
        count = 0

        # get correct font
        if self.game.run_setup.ready_to_start:
            active_font = default_font
        else:
            active_font = disabled_font

        active_font.render("Start run", surface, (current_x, current_y))

        # draw selector
        if count == self.selected_col and current_row == self.selected_row:
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (current_x, current_y + font_height),
                (current_x + default_font.width("home"), current_y + font_height),
            )

    def handle_selection(self):
        # selected home
        if self.selected_row == 0:
            selected_home = self.game.data.homes[self.selected_col]

            # if already using this home unset it
            if self.game.run_setup.selected_ally == selected_home:
                self.game.run_setup.selected_ally = ""

            self.game.run_setup.selected_home = selected_home

        # selected ally
        elif self.selected_row == 1:
            selected_home = self.game.data.homes[self.selected_col]

            # if already using this home unset it
            if self.game.run_setup.selected_home == selected_home:
                self.game.run_setup.selected_home = ""

            self.game.run_setup.selected_ally = selected_home

        # seed
        elif self.selected_row == 2:
            # TODO - allow player to set seed
            pass

        # confirm
        elif self.selected_row == 3:
            # ensure conditions are as we need them
            if self.game.run_setup.ready_to_start:
                self.game.run_setup.start_run()

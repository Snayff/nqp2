from __future__ import annotations

import logging
from typing import TYPE_CHECKING

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

    def update(self):
        num_homes = len(self.game.data.homes)
        dimensions = {
            0: num_homes,
            1: num_homes,
            2: 1,
            3: 1
        }

        self.handle_selection_dimensions(len(dimensions.keys()), dimensions[self.selected_row])
        self.handle_directional_input_for_selection()
        self.handle_selected_index_looping()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            logging.info(
                f"Selected option {self.selected_row},"
                f" {self.game.event.active_event['options'][self.selected_row]}."
            )

            self.game.event.trigger_result(self.selected_row)

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

    def render(self, surface: pygame.surface):
        default_font = self.default_font
        positive_font = self.positive_font

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

            if self.game.run_setup.selected_home == home:
                active_font = positive_font
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

            if self.game.run_setup.selected_ally == home:
                active_font = positive_font
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
        # TODO - convert to input field so player can set seed
        current_x = start_x
        count = 0

        active_font = default_font
        active_font.render("Seed: " + str(self.game.rng.current_seed), surface, (current_x, current_y))

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

        active_font = default_font
        active_font.render("Start run", surface, (current_x, current_y))

        # draw selector
        if count == self.selected_col and current_row == self.selected_row:
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (current_x, current_y + font_height),
                (current_x + default_font.width("home"), current_y + font_height),
            )



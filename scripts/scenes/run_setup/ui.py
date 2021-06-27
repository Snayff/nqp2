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
        options = self.game.event.active_event["options"]

        self.handle_directional_input_for_selection()

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

        # manage looping
        self.handle_selected_index_looping(len(options))

    def render(self, surface: pygame.surface):
        default_font = self.default_font

        # positions
        option_x = 20
        option_start_y = self.game.window.height // 2
        gap = 10
        font_height = 12  # FIXME - get actual font height

        # draw commander options


        # draw aide options


        # draw seed
        # TODO - convert to input field so player can set seed

        # draw confirm option





        # draw description
        default_font.render(event["description"], surface, (10, 0 + 20))

        # draw options
        count = 0
        for option in event["options"]:

            # draw option
            option_y = option_start_y + ((font_height + gap) * count)
            default_font.render(option["text"], surface, (option_x, option_y))

            # draw selector
            if count == self.selected_row:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (option_x, option_y + font_height),
                    (option_x + default_font.width(option["text"]), option_y + font_height),
                )

            count += 1


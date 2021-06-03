from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["EventUI"]


class EventUI(UI):
    """
    Represent the UI of the EventScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_option: int = 0

    def update(self):
        options = self.game.event.active_event["options"]

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_option -= 1

        if self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_option += 1

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            logging.info(
                f"Selected option {self.selected_option},"
                f" {self.game.event.active_event['options'][self.selected_option]}."
            )

            self.game.event.trigger_result(self.selected_option)

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        # correct selection index for looping
        if self.selected_option < 0:
            self.selected_option = len(options) - 1
        if self.selected_option >= len(options):
            self.selected_option = 0

    def render(self, surface: pygame.surface):
        event = self.game.event.active_event
        default_font = self.game.assets.fonts["default"]

        # positions
        option_x = 20
        option_start_y = self.game.window.height // 2
        gap = 10
        font_height = 12  # FIXME - get actual font height

        # draw description
        default_font.render(event["description"], surface, (10, 0 + 20))

        # draw options
        count = 0
        for option in event["options"]:

            # draw option
            option_y = option_start_y + ((font_height + gap) * count)
            default_font.render(option["text"], surface, (option_x, option_y))

            # draw selector
            if count == self.selected_option:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (option_x, option_y + font_height),
                    (option_x + default_font.width(option["text"]), option_y + font_height),
                )

            count += 1

        # show gold
        default_font.render(f"Gold: {self.game.memory.gold}", surface, (1, 1), 2)

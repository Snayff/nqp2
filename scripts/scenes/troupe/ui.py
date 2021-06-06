from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["TroupeUI"]


class TroupeUI(UI):
    """
    Represent the UI of the TroupeScene.
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

        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to previous scene
            self.game.change_scene(self.game.troupe.previous_scene_type)

        # correct selection index for looping
        if self.selected_option < 0:
            self.selected_option = len(options) - 1
        if self.selected_option >= len(options):
            self.selected_option = 0

    def render(self, surface: pygame.surface):
        units = self.game.memory.player_troupe.units
        default_font = self.game.assets.fonts["default"]

        # positions
        start_x = 20
        start_y = self.game.window.height // 2
        unit_width = DEFAULT_IMAGE_SIZE
        unit_height = DEFAULT_IMAGE_SIZE
        section_width = unit_width * 2
        stat_icon_size = (DEFAULT_IMAGE_SIZE // 2, DEFAULT_IMAGE_SIZE // 2)
        stat_height = stat_icon_size[1]
        gap = 10
        font_height = 12  # FIXME - get actual font height

        # draw options
        unit_count = 0
        for unit in units.values():

            # draw icon
            unit_icon_pos = (start_x + (unit_width // 2), start_y + unit_height)
            unit_icon = self.game.assets.get_image("units", "ArcherIcon")
            surface.blit(unit_icon, unit_icon_pos)

            # draw unit info
            info_x = start_x + (section_width * unit_count)

            # draw type
            default_font.render(unit.type, surface, (info_x, start_y + unit_height))

            # draw stats
            stats = [
                "attack",
                "defence",
                "health"
            ]
            stat_count = 1
            for stat in stats:
                info_y = start_y + (stat_height * stat_count)

                stat_icon = self.game.assets.get_image("stats", stat, stat_icon_size)
                surface.blit(stat_icon, (info_x, info_y))
                default_font.render(str(getattr(unit, stat)), surface, (info_x, info_y))

                stat_count += 1


            # draw selector
            # if unit_count == self.selected_option:
            #     pygame.draw.line(
            #         surface,
            #         (255, 255, 255),
            #         (option_x, option_y + font_height),
            #         (option_x + default_font.width(option["text"]), option_y + font_height),
            #     )

            unit_count += 1

        # show gold
        default_font.render(f"Gold: {self.game.memory.gold}", surface, (1, 1), 2)

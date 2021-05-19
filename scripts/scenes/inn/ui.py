from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["InnUI"]


class InnUI(UI):
    """
    Represent the UI of the InnScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_option: int = 0

    def update(self):
        units_for_sale = self.game.inn.units_for_sale

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_option -= 1

        if self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_option += 1

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False
            self.game.inn.purchase_unit(self.selected_option)

        # exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        # correct selection index for looping
        if self.selected_option < 0:
            self.selected_option = len(units_for_sale) - 1
        if self.selected_option >= len(units_for_sale):
            self.selected_option = 0

    def render(self, surface: pygame.surface):
        units_for_sale = self.game.inn.units_for_sale
        font = self.game.assets.fonts["small_red"]
        stats = [
            "health",
            "defense",
            "damage",
            "range",
            "attack_speed",
            "move_speed",
            "ammo",
            "count",
        ]

        # positions
        start_x = 20
        start_y = 60
        gap = 10
        font_height = 12
        window_width = self.game.window.width
        col_width = int((window_width - (start_x * 2)) / len(stats))

        # draw headers
        col_count = 0
        for stat in stats:
            col_x = start_x + (col_width * col_count)
            font.render(stat, surface, (col_x, start_y))

            col_count += 1

        # draw unit info
        row_count = 0
        for unit in units_for_sale:
            name = list(unit)[0]
            details = unit.get(name)

            option_y = start_y + ((font_height + gap) * (row_count + 1))

            # draw stats
            col_count = 0
            for stat in stats:
                col_x = start_x + (col_width * col_count)

                if col_count == 0:
                    text = name
                else:
                    text = str(details.get(stat))

                font.render(text, surface, (col_x, option_y))

                col_count += 1


            # draw selector
            if row_count == self.selected_option:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, option_y + font_height),
                    (start_x + font.width(name), option_y + font_height),
                )

            row_count += 1

            # show gold
            font.render(f"Gold: {self.game.memory.gold}", surface, (0, 0), 2)

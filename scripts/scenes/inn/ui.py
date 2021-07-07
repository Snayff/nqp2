from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["InnUI"]

########### To Do List #############
# TODO - Add button for going back to  overworld


class InnUI(UI):
    """
    Represent the UI of the InnScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.set_instruction_text("Make your purchases.")

    def update(self, delta_time: float):
        super().update(delta_time)

        units_for_sale = self.game.inn.sale_troupe

        self.set_selection_dimensions(len(units_for_sale.units), 1)
        self.handle_directional_input_for_selection()
        self.handle_selector_index_looping()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # can we purchase
            units = list(self.game.inn.sale_troupe.units.values())
            unit = units[self.selected_row]
            can_afford = unit.gold_cost <= self.game.memory.gold
            has_enough_charisma = self.game.memory.commander.charisma_remaining > 0
            if can_afford and has_enough_charisma:
                self.game.inn.purchase_unit(unit)
            else:
                if not can_afford:
                    self.set_instruction_text(f"You can't afford the {unit.type}.", True)
                else:
                    self.set_instruction_text(f"You don't have enough charisma to recruit them.", True)

        # exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.surface):
        units_for_sale = list(self.game.inn.sale_troupe.units.values())
        default_font = self.default_font
        disabled_font = self.disabled_font
        warning_font = self.warning_font

        stats = [
            "type",
            "health",
            "defence",
            "attack",
            "range",
            "attack_speed",
            "move_speed",
            "ammo",
            "count",
            "gold_cost",
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
            default_font.render(stat, surface, (col_x, start_y))

            col_count += 1

        # draw unit info
        row_count = 0
        for unit in units_for_sale:

            # check can purchase
            can_afford = unit.gold_cost <= self.game.memory.gold
            has_enough_charisma = self.game.memory.commander.charisma_remaining > 0
            if can_afford and has_enough_charisma:
                active_font = default_font
            else:
                active_font = disabled_font

            option_y = start_y + ((font_height + gap) * (row_count + 1))  # + 1 due to headers

            # draw stats
            col_count = 0
            for stat in stats:
                col_x = start_x + (col_width * col_count)

                # if can't afford then show cost as red to highlight the issue
                text = str(getattr(unit, stat))
                if active_font == disabled_font and stat == "gold_cost":
                    warning_font.render(text, surface, (col_x, option_y))
                else:
                    active_font.render(text, surface, (col_x, option_y))

                col_count += 1

            # draw selector
            if row_count == self.selected_row:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, option_y + font_height),
                    (start_x + active_font.width(unit.type), option_y + font_height),
                )

            row_count += 1

            # show gold
            self.draw_gold(surface)
            self.draw_charisma(surface)
            self.draw_leadership(surface)
            self.draw_instruction(surface)

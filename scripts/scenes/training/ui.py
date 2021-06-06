from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, SceneType
from scripts.scenes.combat.elements.unit import Unit

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["TrainingUI"]


class TrainingUI(UI):
    """
    Represent the UI of the TrainingScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_option: int = 0

    def update(self):
        units = self.game.memory.player_troupe.units

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_option -= 1

        if self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_option += 1

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False


        # exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.TROUPE)

        # correct selection index for looping
        if self.selected_option < 0:
            self.selected_option = len(units) - 1
        if self.selected_option >= len(units):
            self.selected_option = 0

    def render(self, surface: pygame.surface):
        units = self.game.memory.player_troupe.units
        selected_unit = None
        default_font = self.game.assets.fonts["default"]
        disabled_font = self.game.assets.fonts["disabled"]
        warning_font = self.game.assets.fonts["warning"]
        positive_font = self.game.assets.fonts["positive"]

        # positions
        start_x = 20
        start_y = 20
        select_unit_icon_width = DEFAULT_IMAGE_SIZE
        select_unit_icon_height = DEFAULT_IMAGE_SIZE
        select_unit_icon_size = (select_unit_icon_width, select_unit_icon_height)
        gap = 2
        font_height = 12  # FIXME - get actual font height

        # draw list of unit names
        unit_count = 0
        for unit in units.values():
            # draw icon
            unit_icon_x = start_x
            unit_icon_y = start_y + ((select_unit_icon_height + gap) * unit_count)
            unit_icon_pos = (unit_icon_x, unit_icon_y)
            unit_icon = self.game.assets.get_image("units", unit.type + "_icon", select_unit_icon_size)
            surface.blit(unit_icon, unit_icon_pos)

            # draw unit type
            unit_type_x = unit_icon_x + select_unit_icon_width + gap
            unit_type_y = unit_icon_y + (select_unit_icon_height // 2)

            # determine which font to use
            cost = unit.upgrade_cost
            if cost < self.game.memory.gold and not unit.is_upgraded:
                font = default_font
            else:
                font = disabled_font

            font.render(unit.type, surface, (unit_type_x, unit_type_y))

            # note selected unit
            if self.selected_option == unit_count:
                selected_unit = unit

            # draw selector
            if unit_count == self.selected_option:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (unit_type_x, unit_type_y + font_height),
                    (unit_type_x + default_font.width(unit.type), unit_type_y + font_height),
                )

            unit_count += 1

        # ensure a selected unit is found
        if not selected_unit:
            return

        # get upgrade details
        upgraded_unit = Unit(self.game, -1, selected_unit.type, "player", True)

        # positions
        comparison_x = self.game.window.width // 2
        comparison_y = start_y
        comparison_unit_icon_width = DEFAULT_IMAGE_SIZE * 2
        comparison_unit_icon_height = DEFAULT_IMAGE_SIZE * 2
        comparison_unit_icon_size = (comparison_unit_icon_width, comparison_unit_icon_height)
        stat_width = DEFAULT_IMAGE_SIZE
        stat_height = DEFAULT_IMAGE_SIZE
        stat_icon_size = (stat_width, stat_height)
        section_width = comparison_unit_icon_width * 2

        # show selected unit and upgraded unit details
        unit_count = 0
        for unit in [selected_unit, upgraded_unit]:
            # draw icon
            unit_icon_x = comparison_x + (comparison_unit_icon_width // 2) + (section_width * unit_count)
            unit_icon_pos = (unit_icon_x, comparison_y)
            unit_icon = self.game.assets.get_image("units", unit.type + "_icon", comparison_unit_icon_size)
            surface.blit(unit_icon, unit_icon_pos)

            # draw unit type
            info_x = comparison_x + ((section_width * unit_count) + gap)
            unit_type_y = comparison_y + comparison_unit_icon_height + gap
            default_font.render(unit.type, surface, (info_x, unit_type_y))

            # draw stats
            stats = ["health", "attack", "defence", "range", "attack_speed", "move_speed", "ammo", "count", "size"]
            stat_count = 0
            for stat in stats:
                info_y = unit_type_y + font_height + ((stat_height + gap) * stat_count) + gap
                stat_icon_x = info_x + (stat_width // 2)
                stat_info_x = stat_icon_x + stat_width + 2

                stat_icon = self.game.assets.get_image("stats", stat, stat_icon_size)
                surface.blit(stat_icon, (stat_icon_x, info_y))

                # determine font
                if getattr(selected_unit, stat) < getattr(upgraded_unit, stat):
                    font = positive_font
                else:
                    font = warning_font

                # + half font height to vertical centre it
                font.render(str(getattr(unit, stat)), surface, (stat_info_x, info_y + (font_height // 2)))

                stat_count += 1

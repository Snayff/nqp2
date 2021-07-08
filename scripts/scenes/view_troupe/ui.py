from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["ViewTroupeUI"]


class ViewTroupeUI(UI):
    """
    Represent the UI of the ViewTroupeScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.set_instruction_text(f"Press X to exit the troupe overview.")

    def update(self, delta_time: float):
        super().update(delta_time)

        units = self.game.memory.player_troupe.units

        self.set_element_array_dimensions(1, len(units))
        self.handle_directional_input_for_selection()
        self.handle_selector_index_looping()

        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to previous scene
            self.game.change_scene(self.game.troupe.previous_scene_type)

    def render(self, surface: pygame.surface):
        units = self.game.memory.player_troupe.units
        default_font = self.default_font

        # positions
        start_x = 20
        start_y = 20
        unit_width = DEFAULT_IMAGE_SIZE * 2
        unit_height = DEFAULT_IMAGE_SIZE * 2
        unit_size = (unit_width, unit_height)
        section_width = unit_width * 3
        stat_width = DEFAULT_IMAGE_SIZE
        stat_height = DEFAULT_IMAGE_SIZE
        stat_icon_size = (stat_width, stat_height)
        font_height = 12  # FIXME - get actual font height

        # draw options
        unit_count = 0
        for unit in units.values():

            # draw icon
            unit_icon_x = start_x + (unit_width // 2) + (section_width * unit_count)
            unit_icon_pos = (unit_icon_x, start_y)
            unit_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
            surface.blit(unit_icon, unit_icon_pos)

            # draw unit type
            info_x = start_x + ((section_width * unit_count) + GAP_SIZE)
            unit_type_y = start_y + unit_height + GAP_SIZE
            default_font.render(unit.type, surface, (info_x, unit_type_y))

            # draw stats
            stats = ["health", "attack", "defence", "range", "attack_speed", "move_speed", "ammo", "count", "size"]
            stat_count = 0
            for stat in stats:
                info_y = unit_type_y + font_height + ((stat_height + GAP_SIZE) * stat_count) + GAP_SIZE
                stat_icon_x = info_x + (stat_width // 2)
                stat_info_x = stat_icon_x + stat_width + 2

                stat_icon = self.game.assets.get_image("stats", stat, stat_icon_size)
                surface.blit(stat_icon, (stat_icon_x, info_y))
                # + half font height to vertical centre it
                default_font.render(str(getattr(unit, stat)), surface, (stat_info_x, info_y + (font_height // 2)))

                stat_count += 1

            unit_count += 1

        # show core info
        self.draw_gold(surface)
        self.draw_charisma(surface)
        self.draw_leadership(surface)
        self.draw_instruction(surface)

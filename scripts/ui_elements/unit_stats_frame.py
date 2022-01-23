from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui_element import UIElement
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE, StatModifiedStatus
from scripts.scene_elements.unit import Unit

if TYPE_CHECKING:
    from typing import Tuple

    from scripts.core.game import Game


__all__ = ["UnitStatsFrame"]

########## TO DO LIST ########
# TODO - can this inherit from Frame?


class UnitStatsFrame(UIElement):
    def __init__(self, game: Game, pos: Tuple[int, int], unit: Unit, is_selectable: bool = False):
        super().__init__(pos, is_selectable)

        self._game: Game = game
        self.unit: Unit = unit

        self._rebuild_surface()

    def update(self, delta_time: float):
        pass

    def _rebuild_surface(self):
        # resize surface
        self.surface = pygame.Surface((100, 400))

        surface = self.surface
        unit = self.unit
        start_x = 0
        start_y = 0

        stat_icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        # draw icon
        current_x = start_x
        current_y = start_y
        unit_icon = self._game.assets.unit_animations[unit.type]["icon"][0]
        surface.blit(unit_icon, (current_x, current_y))

        current_y += unit_icon.get_height() + GAP_SIZE

        # draw unit type
        font = self._game.assets.create_font(FontType.DEFAULT, unit.type, (current_x, current_y))
        font.draw(surface)

        current_y += font.height + GAP_SIZE

        # draw stats
        icon_x = current_x
        info_x = current_x + unit_icon.get_width() + GAP_SIZE
        stats = ["health", "attack", "defence", "range", "attack_speed", "move_speed", "ammo", "count", "size"]
        for stat in stats:

            # draw stat icon
            stat_icon = self._game.assets.get_image("stats", stat, stat_icon_size)
            surface.blit(stat_icon, (icon_x, current_y))

            # determine font
            mod_state = unit.get_modified_status(stat)
            if mod_state == StatModifiedStatus.POSITIVE:
                font_type = FontType.POSITIVE
            elif mod_state == StatModifiedStatus.POSITIVE_AND_NEGATIVE:
                font_type = FontType.INSTRUCTION
            elif mod_state == StatModifiedStatus.NEGATIVE:
                font_type = FontType.NEGATIVE
            else:
                font_type = FontType.DEFAULT

            # + half font height to vertical centre it
            font = self._game.assets.create_font(font_type, str(getattr(unit, stat)))
            font.pos = (info_x, current_y + (font.height // 2))
            font.draw(surface)

            # increment y
            current_y += stat_icon_size[1] + GAP_SIZE

    def set_unit(self, unit: Unit):
        self.unit = unit

        self._rebuild_surface()

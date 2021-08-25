from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui_element import UIElement
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, StatModifiedStatus
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import List, Tuple

    from scripts.core.game import Game


__all__ = ["UnitStatsFrame"]

########## TO DO LIST ########
# TODO - can this inherit from Frame?


class UnitStatsFrame(UIElement):
    def __init__(self, game: Game, pos: Tuple[int, int], unit: Unit, is_selectable: bool = False):
        super().__init__(pos, is_selectable)

        self.game: Game = game
        self.unit: Unit = unit

        self.default_font: Font = self.game.assets.fonts["default"]
        self.disabled_font: Font = self.game.assets.fonts["disabled"]
        self.warning_font: Font = self.game.assets.fonts["warning"]
        self.positive_font: Font = self.game.assets.fonts["positive"]
        self.instruction_font: Font = self.game.assets.fonts["instruction"]

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
        default_font = self.default_font
        warning_font = self.warning_font
        positive_font = self.positive_font
        instruction_font = self.instruction_font

        font_height = default_font.height
        stat_icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        # draw icon
        current_x = start_x
        current_y = start_y
        unit_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
        surface.blit(unit_icon, (current_x, current_y))

        current_y += unit_icon.get_height() + GAP_SIZE

        # draw unit type
        default_font.render(unit.type, surface, (current_x, current_y))

        current_y += font_height + GAP_SIZE

        # draw stats
        icon_x = current_x
        info_x = current_x + unit_icon.get_width() + GAP_SIZE
        stats = ["health", "attack", "defence", "range", "attack_speed", "move_speed", "projectiles", "count", "size"]
        for stat in stats:

            # draw stat icon
            stat_icon = self.game.assets.get_image("stats", stat, stat_icon_size)
            surface.blit(stat_icon, (icon_x, current_y))

            # determine font
            mod_state = unit.get_modified_status(stat)
            if mod_state == StatModifiedStatus.POSITIVE:
                font = positive_font
            elif mod_state == StatModifiedStatus.POSITIVE_AND_NEGATIVE:
                font = instruction_font
            elif mod_state == StatModifiedStatus.NEGATIVE:
                font = warning_font
            else:
                font = default_font

            # + half font height to vertical centre it
            font.render(str(getattr(unit, stat)), surface, (info_x, current_y + (font_height // 2)))

            # increment y
            current_y += stat_icon_size[1] + GAP_SIZE

    def set_unit(self, unit: Unit):
        self.unit = unit

        self._rebuild_surface()

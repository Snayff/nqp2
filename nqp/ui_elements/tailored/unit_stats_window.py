from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from nqp.command.unit import Unit
from nqp.core.constants import DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE, StatModifiedStatus, WindowType
from nqp.ui_elements.generic.ui_frame import UIFrame
from nqp.ui_elements.generic.ui_window import UIWindow

if TYPE_CHECKING:
    from typing import Tuple

    from nqp.core.game import Game


__all__ = ["UnitStatsWindow"]


class UnitStatsWindow(UIWindow):
    """
    A UIWindow designed to show the stats for a given Unit.
    """

    def __init__(self, game: Game, pos: Tuple[int, int], unit: Unit, is_active: bool = False):
        size = (100, 200)
        super().__init__(game, WindowType.BASIC, pos, size, [], is_active)

        self._unit: Unit = unit

        self._rebuild_stat_frames()

    def update(self, delta_time: float):
        pass

    def _rebuild_stat_frames(self):
        create_font = self._game.visual.create_font
        create_fancy_font = self._game.visual.create_fancy_font
        create_animation = self._game.visual.create_animation
        get_image = self._game.visual.get_image

        # positions and sizes
        start_x, start_y = self.pos
        stat_icon_size = (DEFAULT_IMAGE_SIZE // 2, DEFAULT_IMAGE_SIZE // 2)
        panel_width, panel_height = self.size

        current_x = start_x
        current_y = start_y

        # draw background
        bg_width = panel_width
        bg_height = panel_height
        bg = pygame.Surface((bg_width, bg_height), SRCALPHA)
        bg.fill((0, 0, 0, 150))
        frame = UIFrame(self._game, (current_x, current_y), image=bg)
        self._elements.append(frame)

        # draw icon
        current_x = start_x
        current_y = start_y
        unit_icon = create_animation(self._unit.type, "icon")
        font = create_fancy_font(self._unit.type, (0, 0))
        frame = UIFrame(self._game, (current_x, current_y), new_image=unit_icon, font=font)
        self._elements.append(frame)

        # increment
        current_y += frame.height + GAP_SIZE

        # draw stats
        stats = ["health", "attack", "defence", "range", "attack_speed", "move_speed", "ammo", "count"]
        for count, stat in enumerate(stats):

            # recalc x and y
            y_mod = count % 4  # this is the rows in the col
            x_mod = count // 4  # must match int used for y
            frame_x = current_x + (x_mod * (stat_icon_size[0] // 2))
            frame_y = current_y + (y_mod * (stat_icon_size[0] // 2))

            # determine font to use
            mod_state = self._unit.get_modified_status(stat)
            if mod_state == StatModifiedStatus.POSITIVE:
                font_type = FontType.POSITIVE
            elif mod_state == StatModifiedStatus.POSITIVE_AND_NEGATIVE:
                font_type = FontType.INSTRUCTION
            elif mod_state == StatModifiedStatus.NEGATIVE:
                font_type = FontType.NEGATIVE
            else:
                font_type = FontType.DEFAULT

            # draw stat icon and info
            stat_icon = get_image(stat, stat_icon_size)
            font = create_font(font_type, str(getattr(self._unit, stat)))
            frame = UIFrame(self._game, (frame_x, frame_y), new_image=stat_icon, font=font)
            self._elements.append(frame)

    def set_unit(self, unit: Unit):
        self._unit = unit

        self._rebuild_stat_frames()

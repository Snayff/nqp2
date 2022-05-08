from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from nqp.command.unit import Unit
from nqp.core.components import Stats
from nqp.core.constants import (
    DEFAULT_IMAGE_SIZE,
    FontType,
    GAP_SIZE,
    StatModifiedStatus,
    TextRelativePosition,
    WindowType,
)
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

    def __init__(self, game: Game, pos: pygame.Vector2, unit: Unit, is_active: bool = False):
        size = pygame.Vector2(100, 160)
        super().__init__(game, WindowType.BASIC, pos, size, [], is_active)

        self.unit: Unit = unit

        self._rebuild_stat_frames()

    def _rebuild_stat_frames(self):
        create_font = self._game.visual.create_font
        create_fancy_font = self._game.visual.create_fancy_font
        create_animation = self._game.visual.create_animation
        get_image = self._game.visual.get_image

        # positions and sizes
        start_x, start_y = self.pos
        stat_icon_size = pygame.Vector2(DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        current_x = start_x + ((self.width // 2) - (stat_icon_size[0] // 2))
        current_y = start_y + 2

        # draw icon
        unit_icon = create_animation(self.unit.type, "icon")
        font = create_fancy_font(self.unit.type, pygame.Vector2(0, 0))
        frame = UIFrame(
            self._game,
            pygame.Vector2(current_x, current_y),
            image=unit_icon,
            font=font,
            text_relative_position=TextRelativePosition.BELOW_IMAGE,
        )
        self._elements.append(frame)

        # increment
        current_x = start_x + GAP_SIZE
        current_y += unit_icon.height + (GAP_SIZE * 2)

        # draw stats
        stats = Stats.get_stat_names()
        stats.remove("weight")  # remove what we dont want to show
        for count, stat in enumerate(stats):

            # recalc x and y
            y_mod = count % 4  # this is the rows in the col
            x_mod = count // 4  # must match int used for y
            frame_x = current_x + (x_mod * (stat_icon_size[0] + GAP_SIZE))
            frame_y = current_y + (y_mod * (stat_icon_size[1] + GAP_SIZE))

            # determine font to use
            mod_state = self.unit.get_modified_status(stat)
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
            font = create_font(font_type, str(getattr(self.unit, stat)))
            frame = UIFrame(
                self._game,
                pygame.Vector2(frame_x, frame_y),
                image=stat_icon,
                font=font,
                is_selectable=True,
                tooltip_key=stat,
            )
            self._elements.append(frame)

    def set_unit(self, unit: Unit):
        self.unit = unit

        self._rebuild_stat_frames()

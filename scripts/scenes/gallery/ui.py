from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE
from scripts.core.utility import next_number_in_loop, previous_number_in_loop
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    import pygame

    from scripts.core.game import Game



__all__ = ["GalleryUI"]


######### TO DO LIST ###############


class GalleryUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self._frame_timer: float = 0
        self._start_index: int = 0
        self._end_index: int = 47
        self._amount_per_page: int = 16

    def update(self, delta_time: float):
        super().update(delta_time)

        max_units = len(self.game.assets.unit_animations)

        if self.game.input.states["left"]:
            self.game.input.states["left"] = False
            # TODO keep start index and end index 47 apart (47 is how many we can show on screen)
            self._start_index = max(self._start_index - 16, 0)
            self._end_index = max(self._end_index - 16, 47)

        if self.game.input.states["right"]:
            self.game.input.states["right"] = False
            self._start_index = min(self._start_index + 16, max_units - 47)
            self._end_index = min(self._end_index + 16, max_units)


        # tick frame
        self._frame_timer += delta_time
        # FIXME - temporary looping frame logic
        while self._frame_timer > 0.66:
            self._frame_timer -= 0.66

    def render(self, surface: pygame.surface):
        default_font = self.default_font
        positive_font = self.positive_font
        units = self.game.data.units
        animations = self.game.assets.unit_animations
        start_index = self._start_index
        end_index = self._end_index

        start_x = 10
        start_y = 10
        current_x = start_x
        current_y = start_y
        x_gap = 2
        y_gap = 4
        name_col_width = (DEFAULT_IMAGE_SIZE * 4) + x_gap
        sprite_col_width = DEFAULT_IMAGE_SIZE + x_gap
        row_height = DEFAULT_IMAGE_SIZE + y_gap

        frame = int(self._frame_timer * 6)

        #       |header| header |header  (etc.)
        # name | icon | idle | move | attack | hit | death

        # draw headers
        anim_states = ["icon", "idle", "walk", "attack", "hit", "death"]
        default_font.render("name", surface, (current_x, current_y))
        current_x += name_col_width
        for header in anim_states:
            default_font.render(header, surface, (current_x, current_y))
            current_x += sprite_col_width

        # reset x and increment y
        current_x = start_x
        current_y += row_height

        # draw name and sprites
        j = 0
        for i, name in enumerate(units.keys()):
            if not (start_index <= i <= end_index):
                continue

            current_x = start_x + (j // self._amount_per_page) * 200
            current_y = start_y + row_height + (j % self._amount_per_page) * 20


            positive_font.render(name, surface, (current_x, current_y))
            current_x += name_col_width

            for animation in anim_states:
                try:
                    frame_ = min(frame, len(animations[name][animation]) - 1)
                    image = animations[name][animation][frame_]
                    surface.blit(image, (current_x, current_y - (default_font.height // 2)))

                except IndexError:
                    pass

                current_x += sprite_col_width

            j += 1

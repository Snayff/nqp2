from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, SceneType
from scripts.core.utility import next_number_in_loop

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    import pygame

    from scripts.core.game import Game
    from scripts.scenes.gallery.scene import GalleryScene


__all__ = ["GalleryUI"]


######### TO DO LIST ###############


class GalleryUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, parent_scene: GalleryScene):
        super().__init__(game, True)
        self.parent_scene: GalleryScene = parent_scene

        self._frame_timer: float = 0
        self._start_index: int = 0
        self._end_index: int = 47  # 47 is max that can be shown on screen, -1 for index
        self._amount_per_col: int = 16
        self._filters = ["all"]
        for faction in self.game.data.factions:
            self._filters.append(faction)
        self._current_filter = "all"

        self.set_instruction_text("Press tab to change filter.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # tick frame
        self._frame_timer += delta_time
        # FIXME - temporary looping frame logic
        while self._frame_timer > 0.66:
            self._frame_timer -= 0.66

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        max_units = len(self.game.assets.unit_animations)

        if self.game.input.states["left"]:
            self.game.input.states["left"] = False
            self._start_index = max(self._start_index - 16, 0)
            self._end_index = max(self._end_index - 16, 47)

        if self.game.input.states["right"]:
            self.game.input.states["right"] = False
            self._start_index = min(self._start_index + 16, max_units - 47)
            self._end_index = min(self._end_index + 16, max_units)

        if self.game.input.states["tab"]:
            self.game.input.states["tab"] = False

            current_filter_index = self._filters.index(self._current_filter)
            next_index = next_number_in_loop(current_filter_index, len(self._filters))
            self._current_filter = self._filters[next_index]

        # exit
        if self.current_panel == self.panels["exit"]:
            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                # return to previous scene
                self.game.change_scene(self.game.dev_gallery.previous_scene_type)

    def render(self, surface: pygame.surface):
        default_font = self.default_font
        positive_font = self.positive_font
        disabled_font = self.disabled_font
        units = self.game.data.units
        animations = self.game.assets.unit_animations
        start_index = self._start_index
        end_index = self._end_index
        window_width = self.game.window.width

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

        # draw headers
        anim_states = ["icon", "idle", "walk", "attack", "hit", "death"]
        disabled_font.render("name", surface, (current_x, current_y))
        current_x += name_col_width
        for header in anim_states:
            disabled_font.render(header, surface, (current_x, current_y))
            current_x += sprite_col_width

        # increment y
        current_y += row_height

        # draw name and sprites
        j = 0
        for i, (name, data) in enumerate(units.items()):
            # only draw units within index range or for whom the filter applies
            is_start_ok = i >= start_index
            is_less_than_end = j < (self._amount_per_col * 3)  # 3 cols
            is_all = self._current_filter == "all"
            is_in_current_filter = data["faction"] == self._current_filter

            if not (is_start_ok and is_less_than_end and (is_all or is_in_current_filter)):
                continue

            current_x = start_x + (j // self._amount_per_col) * 200
            current_y = start_y + row_height + (j % self._amount_per_col) * 20

            default_font.render(name, surface, (current_x, current_y))
            current_x += name_col_width

            for animation in anim_states:
                try:
                    frame_ = min(frame, len(animations[name][animation]) - 1)
                    image = animations[name][animation][frame_]
                    surface.blit(image, (current_x, current_y - (default_font.line_height // 2)))

                except IndexError:
                    pass

                current_x += sprite_col_width

            j += 1

        # count num in filter
        num_in_filter = 0
        if self._current_filter == "all":
            num_in_filter = len(units)
        else:
            for data in units.values():
                if data["faction"] == self._current_filter:
                    num_in_filter += 1

        # draw filter and result number
        num_shown = j
        positive_font.render(
            f"{self._current_filter}. {num_shown}/{num_in_filter}", surface, (window_width - 200, start_y)
        )

        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        self.add_exit_button("Exit")

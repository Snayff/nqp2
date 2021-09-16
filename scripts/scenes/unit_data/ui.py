from __future__ import annotations

import json
import logging
from statistics import mean
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DATA_PATH, DEFAULT_IMAGE_SIZE
from scripts.ui_elements.button import Button
from scripts.ui_elements.input_box import InputBox

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["UnitDataUI"]


class UnitDataUI(UI):
    """
    Represent the UI of the UnitDataScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        window_width = self.game.window.width
        window_height = self.game.window.height

        self.buttons: Dict[str, Button] = {
            "left_arrow": Button(
                game, pygame.transform.flip(self.game.assets.get_image("ui", "arrow_button"), True, False), (10, 10)
            ),
            "right_arrow": Button(game, self.game.assets.get_image("ui", "arrow_button"), (120, 10)),
            "save": Button(game, "save", (window_width - 32, window_height - 22), size=[30, 20]),
            "cancel": Button(game, "cancel", (2, window_height - 22), size=[30, 20]),
        }

        self.fields = {}
        self.unit_list = list(self.game.data.units)
        self.unit_index = 0
        self.current_unit = 0
        self.current_unit_data = {}

        self.tier1_metrics = {}
        self.tier2_metrics = {}
        self.tier3_metrics = {}
        self.tier4_metrics = {}

        self.confirmation_timer = 0
        self.show_confirmation = True
        self.frame_timer = 0
        self.frame_counter = 0

        self.refresh_unit_fields(self.unit_list[self.unit_index])
        self.calculate_unit_metrics()

    def update(self, delta_time: float):
        super().update(delta_time)

        # handle button presses
        buttons = self.buttons
        for button in buttons.values():
            button.update(delta_time)
            if button.pressed:
                if button == buttons["right_arrow"]:
                    self.unit_index += 1
                    if self.unit_index >= len(self.unit_list):
                        self.unit_index = 0
                if button == buttons["left_arrow"]:
                    self.unit_index -= 1
                    if self.unit_index < 0:
                        self.unit_index = len(self.unit_list) - 1
                if button in [buttons["right_arrow"], buttons["left_arrow"]]:
                    self.refresh_unit_fields(self.unit_list[self.unit_index])

                if button == buttons["save"]:
                    for field in self.current_unit_data:
                        self.current_unit_data[field] = self.fields[field].value

                    self.save()

                    # update metrics
                    self.calculate_unit_metrics()

                if button == buttons["cancel"]:
                    # go back to previous scene
                    self.game.change_scene(self.game.dev_unit_data.previous_scene_type)

        # update text fields
        for field in self.current_unit_data:
            self.fields[field].update(delta_time)
            if self.fields[field].should_focus:
                self.fields[field].focus()
            else:
                self.fields[field].unfocus()

        # update confirmation timer
        if self.confirmation_timer > 0:
            self.confirmation_timer -= 1
        else:
            self.show_confirmation = False

        self.frame_timer += 1
        if self.frame_timer > 20:
            self.frame_timer = 0
            self.frame_counter += 1

            if self.frame_counter > 4:
                self.frame_counter = 0

    def render(self, surface: pygame.surface):
        default_font = self.game.assets.fonts["default"]
        positive_font = self.game.assets.fonts["positive"]
        disabled_font = self.game.assets.fonts["disabled"]

        window_width = self.game.window.width
        window_height = self.game.window.height
        font_height = default_font.line_height
        metric_col_width = 80
        metric_second_row_start_y = window_height // 2

        # draw fields and their titles
        default_font.render(self.current_unit, surface, (76 - default_font.width(self.current_unit) // 2, 15))
        for field in self.current_unit_data:
            default_font.render(field, surface, (self.fields[field].pos[0] - 90, self.fields[field].pos[1] + 3))
            self.fields[field].render(surface)

        # draw unit animations
        frame = self.frame_counter
        current_img_x = 150
        current_img_y = 10
        unit_type = self.current_unit_data["type"]
        try:
            for animation_name in ["icon", "idle", "walk", "attack", "hit", "death"]:
                num_frames = len(self.game.assets.unit_animations[unit_type][animation_name])
                frame_ = min(frame, num_frames - 1)
                img = self.game.assets.unit_animations[unit_type][animation_name][frame_]
                img_ = pygame.transform.scale(img, (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE))
                surface.blit(img_, (current_img_x, current_img_y))

                current_img_x += DEFAULT_IMAGE_SIZE + 2
        except KeyError:
            pass

        # draw buttons
        for button in self.buttons.values():
            button.render(surface)

        # show confirmation message
        if self.show_confirmation:
            msg = "Save successful."
            text_width = default_font.width(msg)
            positive_font.render(msg, surface, (window_width - text_width - 35, window_height - font_height))
            # 32 = button width + 5

        # set positions
        start_x = window_width - (window_width // 2.8)
        start_y = 40

        # draw headers
        current_x = start_x + metric_col_width
        current_y = start_y
        for tier_title in ["Tier 1", "Tier 2"]:
            disabled_font.render(tier_title, surface, (current_x, current_y))
            current_x += metric_col_width

        # draw second row headers
        current_x = start_x + metric_col_width
        current_y = metric_second_row_start_y
        for tier_title in ["Tier 3", "Tier 4"]:
            disabled_font.render(tier_title, surface, (current_x, current_y))
            current_x += metric_col_width

        # draw stat list
        current_x = start_x
        current_y = start_y + font_height
        for stat in self.tier1_metrics.keys():
            disabled_font.render(stat, surface, (current_x, current_y))
            current_y += font_height

        # draw stat list for second row
        current_x = start_x
        current_y = metric_second_row_start_y + font_height
        for stat in self.tier1_metrics.keys():
            disabled_font.render(stat, surface, (current_x, current_y))
            current_y += font_height

        # show info regarding other units
        current_x = start_x + metric_col_width
        current_y = start_y + font_height
        for tier in [self.tier1_metrics, self.tier2_metrics]:
            for stat_value in tier.values():
                disabled_font.render(str(stat_value), surface, (current_x, current_y))
                current_y += font_height

            current_x += metric_col_width
            current_y = start_y + font_height

        # show info regarding other units on second row
        current_x = start_x + metric_col_width
        current_y = metric_second_row_start_y + font_height
        for tier in [self.tier3_metrics, self.tier4_metrics]:
            for stat_value in tier.values():
                disabled_font.render(str(stat_value), surface, (current_x, current_y))
                current_y += font_height

            current_x += metric_col_width
            current_y = metric_second_row_start_y + font_height

    def refresh_unit_fields(self, unit_id):
        self.current_unit = unit_id
        self.current_unit_data = self.game.data.units[unit_id]
        self.game.input.mode = "default"

        self.fields = {}
        for i, field in enumerate(self.current_unit_data):
            y = i % 15  # this is the rows in the col
            x = i // 15  # must match int used for y
            self.fields[field] = InputBox(
                self.game,
                [80, 16],
                pos=[100 + x * 200, 30 + y * 20],
                input_type="detect",
                text=self.current_unit_data[field],
            )

    def save(self):
        """
        Save the current unit data to the json.
        """
        unit_type = self.current_unit_data["type"]
        str_path = str(DATA_PATH / "units" / f"{unit_type}.json")

        with open(str_path, "w") as file:
            json.dump(self.current_unit_data, file, indent=4)
            logging.info(f"UnitDataUI: updated {unit_type}; new data saved.")

        # trigger confirmation message
        self.show_confirmation = True
        self.confirmation_timer = 800

    def calculate_unit_metrics(self):
        """
        Calculate useful info.
        """
        tier1 = {}
        tier2 = {}
        tier3 = {}
        tier4 = {}

        # get data sorted by stat
        for unit in self.game.data.units.values():
            if unit["tier"] == 1:
                current_dict = tier1
            elif unit["tier"] == 2:
                current_dict = tier2
            elif unit["tier"] == 3:
                current_dict = tier3
            else:
                # unit["tier"] == 4:
                current_dict = tier4

            # add all units stats to stat lists
            for stat, value in unit.items():
                # ignore strings and tier
                if isinstance(value, str) or stat == "tier":
                    continue

                # init list
                if stat not in current_dict:
                    current_dict[stat] = [value]
                else:
                    current_dict[stat].append(value)

        tier1_calc = {}
        tier2_calc = {}
        tier3_calc = {}
        tier4_calc = {}

        # do calculations
        for stat, values in tier1.items():
            min_ = min(values)
            avg = format(mean(values), ".2f")
            max_ = max(values)
            tier1_calc[stat] = [min_, avg, max_]

        for stat, values in tier2.items():
            min_ = min(values)
            avg = format(mean(values), ".2f")
            max_ = max(values)
            tier2_calc[stat] = [min_, avg, max_]

        for stat, values in tier3.items():
            min_ = min(values)
            avg = format(mean(values), ".2f")
            max_ = max(values)
            tier3_calc[stat] = [min_, avg, max_]

        for stat, values in tier4.items():
            min_ = min(values)
            avg = format(mean(values), ".2f")
            max_ = max(values)
            tier4_calc[stat] = [min_, avg, max_]

        # overwrite attributes
        self.tier1_metrics = tier1_calc
        self.tier2_metrics = tier2_calc
        self.tier3_metrics = tier3_calc
        self.tier4_metrics = tier4_calc

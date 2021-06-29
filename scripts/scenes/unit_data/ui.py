from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DATA_PATH
from scripts.ui_elements.button import Button
from scripts.ui_elements.input_box import InputBox

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["UnitDataUI"]


class UnitDataUI(UI):
    """
    Represent the UI of the UnitDataScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.buttons = {
            "left_arrow": Button(game,
                                 pygame.transform.flip(self.game.assets.get_image("ui", "arrow_button"),
                                                       True, False),
                                 (10, 10)),
            "right_arrow": Button(game, self.game.assets.get_image("ui", "arrow_button"), (120, 10)),
            "save": Button(game, "save", (400, 300), size=[30, 20]),
            "cancel": Button(game, "cancel", (100, 300), size=[30, 20])
        }

        self.fields = {}

        self.unit_list = list(self.game.data.units)
        self.unit_index = 0
        self.current_unit = 0
        self.current_unit_data = {}

        self.load_unit(self.unit_list[self.unit_index])

    def update(self):
        # handle button presses
        buttons = self.buttons
        for button in buttons.values():
            button.update()
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
                    self.load_unit(self.unit_list[self.unit_index])

                if button == buttons["save"]:
                    for field in self.current_unit_data:
                        self.current_unit_data[field] = self.fields[field].value

                    print(self.current_unit_data)
                    self.save()

                if button == buttons["cancel"]:
                    # go back to previous scene
                    self.game.change_scene(self.game.dev_unit_data.previous_scene_type)

        # update text fields
        for field in self.current_unit_data:
            self.fields[field].update()
            if self.fields[field].should_focus:
                self.fields[field].focus()
            else:
                self.fields[field].unfocus()

    def render(self, surface: pygame.surface):
        default_font = self.game.assets.fonts["default"]

        default_font.render(
            self.current_unit,
            surface,
            (76 - default_font.width(self.current_unit) // 2, 15)
        )
        for field in self.current_unit_data:
            default_font.render(field, surface, (self.fields[field].pos[0] - 90, self.fields[field].pos[1] + 3))
            self.fields[field].render(surface)

        for button in self.buttons.values():
            button.render(surface)

    def load_unit(self, unit_id):
        self.current_unit = unit_id
        self.current_unit_data = self.game.data.units[unit_id]
        self.game.input.mode = "default"

        self.fields = {}
        for i, field in enumerate(self.current_unit_data):
            y = i % 10
            x = i // 10
            self.fields[field] = InputBox(
                self.game,
                [80, 16],
                pos=[100 + x * 200, 30 + y * 20],
                input_type="detect",
                text=self.current_unit_data[field]
            )

    def save(self):
        unit_type = self.current_unit_data["type"]
        str_path = str(DATA_PATH / "units" / f"{unit_type}.json")

        with open(str_path, "w") as file:
            json.dump(self.current_unit_data, file, indent=4)
            logging.info(f"UnitDataUI: updated {unit_type}; new data saved.")

from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["RunSetupUI"]


class RunSetupUI(UI):
    """
    Represent the UI of the RunSetupScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        num_commanders = len(self.game.data.commanders)
        self.dimensions: Dict[int, int] = {
            0: num_commanders,
            1: 1,
        }  # row number: number of columns

        self.set_instruction_text("Choose who will lead the rebellion.")

    def update(self, delta_time: float):
        super().update(delta_time)

        self.set_selection_dimensions(len(self.dimensions.keys()), self.dimensions[self.selected_row])
        self.handle_directional_input_for_selection()
        self.handle_selected_index_looping()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            self.handle_selection()

        if self.game.input.states["toggle_data_editor"]:
            self.game.input.states["toggle_data_editor"] = False

            self.game.change_scene(SceneType.DEV_UNIT_DATA)

    def render(self, surface: pygame.surface):
        default_font = self.default_font
        positive_font = self.positive_font
        disabled_font = self.disabled_font

        commanders = self.game.data.commanders
        selected_commander = self.game.run_setup.selected_commander
        current_row = 0

        # positions
        start_x = 20
        start_y = 20
        gap = 10
        font_height = 12  # FIXME - get actual font height
        window_width = self.game.window.width
        window_height = self.game.window.height

        # draw commanders
        sel_col_count = 0
        current_x = start_x
        current_y = start_y
        for commander in commanders.values():
            # get icon and details
            icon_pos = (current_x, current_y)
            icon = self.game.assets.commander_animations[commander["type"]]["icon"][0]
            icon_width = icon.get_width()
            icon_height = icon.get_height()

            # highlight if selected
            if selected_commander == commander["type"]:
                pygame.draw.rect(surface, (252, 211, 3), (icon_pos, (icon_width, icon_height)))

            # draw icon
            surface.blit(icon, icon_pos)

            # draw selector
            if sel_col_count == self.selected_col and current_row == self.selected_row:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (current_x, current_y + icon_height + 2),
                    (current_x + icon_width, current_y + icon_height + 2),
                )

            # increment draw pos and counter
            current_x += icon_width + gap
            sel_col_count += 1

        # draw info
        commander = commanders[selected_commander]
        current_y = start_y + DEFAULT_IMAGE_SIZE + gap
        info_x = start_x + 200
        header_x = start_x

        # name
        default_font.render("Name", surface, (header_x, current_y))
        default_font.render(commander["type"], surface, (info_x, current_y))

        current_y += font_height + gap

        # backstory - N.B. no header
        disabled_font.render(commander["backstory"], surface, (header_x, current_y))

        current_y += font_height + gap

        # limits
        default_font.render("Charisma", surface, (header_x, current_y))
        default_font.render(commander["charisma"], surface, (info_x, current_y))
        current_y += font_height
        default_font.render("Leadership", surface, (header_x, current_y))
        default_font.render(commander["leadership"], surface, (info_x, current_y))

        current_y += font_height + gap

        # allies
        allies = ""
        for ally in commander["allies"]:
            # add comma
            if allies == "":
                allies += ally
            else:
                allies += ", " + ally

        default_font.render("Allies", surface, (header_x, current_y))
        default_font.render(allies, surface, (info_x, current_y))

        current_y += font_height + gap

        # gold
        default_font.render("Gold", surface, (header_x, current_y))
        default_font.render(commander["starting_gold"], surface, (info_x, current_y))

        # draw confirm button
        confirm_text = "begin"
        confirm_width = default_font.width(confirm_text)
        current_x = window_width - (confirm_width + gap)
        current_y = window_height - (font_height + gap)
        default_font.render(confirm_text, surface, (current_x, current_y))

        # draw selector if confirm selected
        current_row += 1
        if current_row == self.selected_row:
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (current_x, current_y + font_height),
                (current_x + confirm_width, current_y + font_height),
            )

        self.draw_instruction(surface)

    def handle_selection(self):
        # select commander
        if self.selected_row == 0:
            selected_commander = list(self.game.data.commanders)[self.selected_col]

            # if selecting same commander then go to begin, else select
            if self.game.run_setup.selected_commander == selected_commander:
                self.selected_row += 1
            else:
                self.game.run_setup.selected_commander = selected_commander

        # begin
        elif self.selected_row == 1:
            self.game.run_setup.start_run()

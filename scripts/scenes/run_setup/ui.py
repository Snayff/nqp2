from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, SceneType
from scripts.ui_elements.frame import Frame

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["RunSetupUI"]


class RunSetupUI(UI):
    """
    Represent the UI of the RunSetupScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.rebuild_selection_array(len(self.game.data.commanders), 10)

        self.set_instruction_text("Choose who will lead the rebellion.")

    def update(self, delta_time: float):
        super().update(delta_time)


        self.handle_directional_input_for_selection()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            self.handle_selection()

        if self.game.input.states["toggle_data_editor"]:
            self.game.input.states["toggle_data_editor"] = False

            self.game.change_scene(SceneType.DEV_UNIT_DATA)

    def render(self, surface: pygame.surface):

        self.draw_instruction(surface)
        self.draw_element_array(surface)

    def rebuild_ui(self):
        commanders = self.game.data.commanders
        selected_commander = self.game.run_setup.selected_commander

        # positions
        start_x = 20
        start_y = 20
        gap = 10
        font_height = 12  # FIXME - get actual font height
        window_width = self.game.window.width
        window_height = self.game.window.height
        frame_width = 75

        # draw commanders
        current_x = start_x
        current_y = start_y
        for selection_counter, commander in enumerate(commanders.values()):
            icon = self.game.assets.commander_animations[commander["type"]]["icon"][0]
            icon_width = icon.get_width()
            icon_height = icon.get_height()
            frame = Frame(
                self.game,
                (current_x, current_y),
                (icon_width, icon_height),
                icon,
                is_selectable=True
            )
            self.element_array[selection_counter][0] = frame

            # show selected commander
            if commander["type"] == selected_commander or selected_commander is None:
                frame.is_selected = True

            # increment draw pos and counter
            current_x += icon_width + gap

        # draw info
        commander = commanders[selected_commander]
        current_y = start_y + DEFAULT_IMAGE_SIZE + gap
        info_x = start_x + 200
        header_x = start_x
        row_counter = 1

        # name
        self.element_array[0][row_counter] = Frame(
            self.game,
            (header_x, current_y),
            (frame_width, font_height),
            text="Name"
        )
        self.element_array[1][row_counter] = Frame(
            self.game,
            (info_x, current_y),
            (frame_width, font_height),
            text=commander["type"]
        )

        current_y += font_height + gap
        row_counter += 1

        # backstory - N.B. no header and needs wider frame
        self.element_array[1][row_counter] = Frame(
            self.game,
            (header_x, current_y),
            (frame_width * 3, font_height),
            text=commander["backstory"]
        )

        current_y += font_height + gap
        row_counter += 1

        # limits
        self.element_array[0][row_counter] = Frame(
            self.game,
            (header_x, current_y),
            (frame_width, font_height),
            text="Charisma"
        )
        self.element_array[1][row_counter] = Frame(
            self.game,
            (info_x, current_y),
            (frame_width, font_height),
            text=commander["charisma"]
        )

        current_y += font_height
        row_counter += 1

        self.element_array[0][row_counter] = Frame(
            self.game,
            (header_x, current_y),
            (frame_width, font_height),
            text="Leadership"
        )
        self.element_array[1][row_counter] = Frame(
            self.game,
            (info_x, current_y),
            (frame_width, font_height),
            text=commander["leadership"]
        )

        current_y += font_height + gap
        row_counter += 1

        # allies
        allies = ""
        for ally in commander["allies"]:
            # add comma
            if allies == "":
                allies += ally
            else:
                allies += ", " + ally
        self.element_array[0][row_counter] = Frame(
            self.game,
            (header_x, current_y),
            (frame_width, font_height),
            text="Allies"
        )
        self.element_array[1][row_counter] = Frame(
            self.game,
            (info_x, current_y),
            (frame_width, font_height),
            text=allies
        )

        current_y += font_height + gap
        row_counter += 1

        # gold
        self.element_array[0][row_counter] = Frame(
            self.game,
            (header_x, current_y),
            (frame_width, font_height),
            text="Gold"
        )
        self.element_array[1][row_counter] = Frame(
            self.game,
            (info_x, current_y),
            (frame_width, font_height),
            text=commander["starting_gold"]
        )

        row_counter += 1

        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + gap)
        current_y = window_height - (font_height + gap)
        self.element_array[0][row_counter] = Frame(self.game,
                                                   (current_x, current_y),
                                                   (confirm_width + 1, font_height),
                                                   text=confirm_text,
                                                   is_selectable=True
                                                   )

    def handle_selection(self):
        # select commander
        if self.selected_row == 0:
            selected_commander = list(self.game.data.commanders)[self.selected_col]

            # if selecting same commander then go to begin, else select
            if self.game.run_setup.selected_commander == selected_commander:
                self.selected_col = 0  # set to first col
                self.increment_selected_row()
            else:
                self.game.run_setup.selected_commander = selected_commander
                self.rebuild_ui()

        # begin
        elif self.selected_row == 7:
            self.game.run_setup.start_run()

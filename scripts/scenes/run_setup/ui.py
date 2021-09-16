from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["RunSetupUI"]


class RunSetupUI(UI):
    """
    Represent the UI of the RunSetupScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.set_instruction_text("Choose who will lead the rebellion.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # data editor
        if self.game.input.states["toggle_dev_console"]:
            self.game.input.states["toggle_dev_console"] = False

            self.game.change_scene(SceneType.DEV_DATA_EDITOR)

        # panel specific input
        if self.current_panel == self.panels["commanders"]:
            self.handle_select_commander_input()

        # exit panel
        elif self.current_panel == self.panels["exit"]:
            self.handle_exit_input()

    def render(self, surface: pygame.surface):

        self.draw_instruction(surface)
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        commanders = self.game.data.commanders
        selected_commander = self.game.run_setup.selected_commander
        default_font = self.default_font

        # positions
        start_x = 20
        start_y = 20
        font_height = default_font.line_height
        window_width = self.game.window.width
        window_height = self.game.window.height

        # draw commanders
        current_x = start_x
        current_y = start_y
        panel_elements = []
        for selection_counter, commander in enumerate(commanders.values()):
            icon = self.game.assets.commander_animations[commander["type"]]["icon"][0]
            icon_width = icon.get_width()
            icon_height = icon.get_height()
            frame = Frame((current_x, current_y), icon, is_selectable=True)
            self.elements[commander["type"]] = frame

            # highlight selected commander
            if commander["type"] == selected_commander or selected_commander is None:
                frame.is_selected = True

            panel_elements.append(frame)

            # increment draw pos and counter
            current_x += icon_width + GAP_SIZE

        panel = Panel(panel_elements, True)
        self.add_panel(panel, "commanders")

        # draw info
        commander = commanders[selected_commander]
        current_y = start_y + DEFAULT_IMAGE_SIZE + GAP_SIZE
        info_x = start_x + 200
        header_x = start_x
        row_counter = 1

        # name
        frame = Frame((header_x, current_y), text_and_font=("Name", default_font))
        self.elements["name_header"] = frame

        frame = Frame((info_x, current_y), text_and_font=(commander["name"], default_font))
        self.elements["name"] = frame

        current_y += font_height + GAP_SIZE
        row_counter += 1

        # backstory - N.B. no header and needs wider frame
        line_width = window_width - (current_x * 2)
        frame = Frame(
            (header_x, current_y), text_and_font=(commander["backstory"], default_font), max_line_width=line_width
        )
        self.elements["backstory"] = frame

        current_y += frame.height + GAP_SIZE
        row_counter += 1

        # limits
        frame = Frame((header_x, current_y), text_and_font=("Charisma", default_font))
        self.elements["charisma_header"] = frame

        frame = Frame((info_x, current_y), text_and_font=(commander["charisma"], default_font))
        self.elements["charisma"] = frame

        current_y += font_height
        row_counter += 1

        frame = Frame((header_x, current_y), text_and_font=("Leadership", default_font))
        self.elements["leadership_header"] = frame

        frame = Frame((info_x, current_y), text_and_font=(commander["leadership"], default_font))
        self.elements["leadership"] = frame

        current_y += font_height + GAP_SIZE
        row_counter += 1

        # allies
        allies = ""
        for ally in commander["allies"]:
            # add comma
            if allies == "":
                allies += ally
            else:
                allies += ", " + ally
        frame = Frame((header_x, current_y), text_and_font=("Allies", default_font))
        self.elements["allies_header"] = frame

        frame = Frame((info_x, current_y), text_and_font=(allies, default_font))
        self.elements["allies"] = frame

        current_y += font_height + GAP_SIZE
        row_counter += 1

        # gold
        frame = Frame((header_x, current_y), text_and_font=("Gold", default_font))
        self.elements["gold_header"] = frame

        frame = Frame((info_x, current_y), text_and_font=(commander["gold"], default_font))
        self.elements["gold"] = frame

        row_counter += 1

        panel_elements = []
        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (font_height + GAP_SIZE)
        frame = Frame((current_x, current_y), text_and_font=(confirm_text, default_font), is_selectable=True)
        self.elements["exit"] = frame
        panel_elements.append(frame)
        panel = Panel(panel_elements, True)
        self.add_panel(panel, "exit")

    def refresh_info(self):
        elements = self.elements
        commander = self.game.data.commanders[self.game.run_setup.selected_commander]

        elements["gold"].set_text(commander["gold"])
        elements["leadership"].set_text(commander["leadership"])
        elements["charisma"].set_text(commander["charisma"])
        elements["backstory"].set_text(commander["backstory"])
        elements["name"].set_text(commander["name"])

        allies = ""
        for ally in commander["allies"]:
            # add comma
            if allies == "":
                allies += ally
            else:
                allies += ", " + ally
        elements["allies"].set_text(allies)

    def handle_select_commander_input(self):
        # selections within panel
        if self.game.input.states["left"]:
            self.game.input.states["left"] = False

            self.current_panel.select_previous_element()

            # update selected commander and shown info
            selected_commander = list(self.game.data.commanders)[self.current_panel.selected_index]
            self.game.run_setup.selected_commander = selected_commander
            self.refresh_info()

        if self.game.input.states["right"]:
            self.game.input.states["right"] = False

            self.current_panel.select_next_element()

            # update selected commander and shown info
            selected_commander = list(self.game.data.commanders)[self.current_panel.selected_index]
            self.game.run_setup.selected_commander = selected_commander
            self.refresh_info()

        # select option and move to exit
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            self.select_panel("exit")

    def handle_exit_input(self):
        if self.game.input.states["select"]:
            self.game.run_setup.start_run()

        if self.game.input.states["cancel"]:
            # unselect current option
            self.current_panel.unselect_all_elements()

            # change to commanders
            self.current_panel = self.panels["commanders"]

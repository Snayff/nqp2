from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontEffects, FontType, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game
    from scripts.scenes.run_setup.scene import RunSetupScene

__all__ = ["RunSetupUI"]


class RunSetupUI(UI):
    """
    Represent the UI of the RunSetupScene.
    """

    def __init__(self, game: Game, parent_scene: RunSetupScene):
        super().__init__(game, True)
        self._parent_scene: RunSetupScene = parent_scene

        self.set_instruction_text("Choose who will lead the rebellion.")

    def update(self, delta_time: float):
        super().update(delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        if self._game.input.states["toggle_dev_console"]:
            self._game.input.states["toggle_dev_console"] = False

            self._game.change_scene(SceneType.DEV_DATA_EDITOR)

        # panel specific input
        if self._current_panel == self._panels["commanders"]:
            self._handle_select_commander_input()

        # exit panel
        elif self._current_panel == self._panels["exit"]:
            self._handle_exit_input()

    def draw(self, surface: pygame.surface):

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        commanders = self._game.data.commanders
        selected_commander = self._game.run_setup.selected_commander
        window_width = self._game.window.width
        window_height = self._game.window.height
        create_font = self._game.assets.create_font
        create_fancy_font = self._game.assets.create_fancy_font

        # positions
        start_x = 20
        start_y = 20
        default_font = self._game.assets.create_font(FontType.DEFAULT, "")
        font_height = default_font.line_height

        # draw commanders
        current_x = start_x
        current_y = start_y
        panel_elements = []
        for selection_counter, commander in enumerate(commanders.values()):
            icon = self._game.assets.commander_animations[commander["type"]]["icon"][0]
            icon_width = icon.get_width()
            frame = Frame((current_x, current_y), icon, is_selectable=True)
            self._elements[commander["type"]] = frame

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

        # name
        frame = Frame((header_x, current_y), font=create_font(FontType.DISABLED, "Name"), is_selectable=False)
        self._elements["name_header"] = frame

        frame = Frame((info_x, current_y), font=create_font(FontType.DEFAULT, commander["name"]), is_selectable=False)
        self._elements["name"] = frame

        current_y += frame.height + GAP_SIZE

        # backstory - N.B. no header and needs wider frame
        line_width = window_width - (current_x * 2)
        max_height = 110
        frame = Frame(
            (header_x, current_y),
            font=create_fancy_font(commander["backstory"], font_effects=[FontEffects.FADE_IN]),
            is_selectable=False,
            max_width=line_width,
            max_height=max_height,
        )
        self._elements["backstory"] = frame

        current_y += frame.height + GAP_SIZE

        # resources
        frame = Frame((header_x, current_y), font=create_font(FontType.DISABLED, "Charisma"), is_selectable=False)
        self._elements["charisma_header"] = frame

        frame = Frame(
            (info_x, current_y), font=create_font(FontType.DEFAULT, commander["charisma"]), is_selectable=False
        )
        self._elements["charisma"] = frame

        current_y += frame.height + GAP_SIZE

        frame = Frame((header_x, current_y), font=create_font(FontType.DISABLED, "Leadership"), is_selectable=False)
        self._elements["leadership_header"] = frame

        frame = Frame(
            (info_x, current_y), font=create_font(FontType.DEFAULT, commander["leadership"]), is_selectable=False
        )
        self._elements["leadership"] = frame

        current_y += frame.height + GAP_SIZE

        # allies
        frame = Frame((header_x, current_y), font=create_font(FontType.DISABLED, "Allies"), is_selectable=False)
        self._elements["allies_header"] = frame

        allies = ""
        for ally in commander["allies"]:
            # add comma
            if allies == "":
                allies += ally
            else:
                allies += ", " + ally
        frame = Frame((info_x, current_y), font=create_font(FontType.DEFAULT, allies), is_selectable=False)
        self._elements["allies"] = frame

        current_y += frame.height + GAP_SIZE

        # gold
        frame = Frame((header_x, current_y), font=create_font(FontType.DISABLED, "Gold"), is_selectable=False)
        self._elements["gold_header"] = frame

        frame = Frame((info_x, current_y), font=create_font(FontType.DEFAULT, commander["gold"]), is_selectable=False)
        self._elements["gold"] = frame

        self.add_exit_button()

    def refresh_info(self):
        elements = self._elements
        commander = self._game.data.commanders[self._game.run_setup.selected_commander]

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

    def _handle_select_commander_input(self):
        # selections within panel
        if self._game.input.states["left"]:
            self._game.input.states["left"] = False

            self._current_panel.select_previous_element()

            # update selected commander and shown info
            selected_commander = list(self._game.data.commanders)[self._current_panel.selected_index]
            self._game.run_setup.selected_commander = selected_commander
            self.refresh_info()

        if self._game.input.states["right"]:
            self._game.input.states["right"] = False

            self._current_panel.select_next_element()

            # update selected commander and shown info
            selected_commander = list(self._game.data.commanders)[self._current_panel.selected_index]
            self._game.run_setup.selected_commander = selected_commander
            self.refresh_info()

        # select option and move to exit
        if self._game.input.states["select"]:
            self._game.input.states["select"] = False

            self.select_panel("exit")

    def _handle_exit_input(self):
        if self._game.input.states["select"]:
            self._game.run_setup.start_run()

        if self._game.input.states["cancel"]:
            # unselect current option
            self._current_panel.unselect_all_elements()

            # change to commanders
            self._current_panel = self._panels["commanders"]

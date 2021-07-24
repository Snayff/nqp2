from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["EventUI"]


class EventUI(UI):
    """
    Represent the UI of the EventScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.set_instruction_text("Choose what to do next.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # generic input
        # selection in panel
        if self.game.input.states["down"]:
            self.game.input.states["down"] = False

            self.current_panel.select_next_element()

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False

            self.current_panel.select_previous_element()

        # view troupe
        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

        # panel specific input
        if self.current_panel == self.panels["options"]:
            self.handle_options_input()

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        event = self.game.event.active_event
        default_font = self.default_font

        # positions
        start_x = 20
        start_y = 50
        font_height = 12  # FIXME - get actual font height

        # draw description
        current_x = start_x
        current_y = start_y
        frame = Frame((current_x, current_y), text_and_font=(event["description"], default_font))
        self.elements["description"] = frame

        # draw options
        current_y = self.game.window.height // 2
        panel_list = []
        for counter, option in enumerate(event["options"]):

            frame = Frame((current_x, current_y), text_and_font=(option["text"], default_font), is_selectable=True)
            self.elements[f"option_{counter}"] = frame
            panel_list.append(frame)

            # increment position
            current_y += frame.height + GAP_SIZE

        # create panel
        panel = Panel(panel_list, True)
        self.add_panel(panel, "options")

        self.rebuild_resource_elements()

    def handle_options_input(self):
        options = self.game.event.active_event["options"]

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            index = self.current_panel.selected_index
            logging.info(f"Selected option {index}, {self.game.event.active_event['options'][index]}.")

            self.game.event.trigger_result(index)

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

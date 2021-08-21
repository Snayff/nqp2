from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, EventState, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import List

    from scripts.core.game import Game

__all__ = ["EventUI"]


class EventUI(UI):
    """
    Represent the UI of the EventScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_option: str = ""  # the option selected

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

        elif self.current_panel == self.panels["exit"]:

            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                self.game.change_scene(SceneType.OVERWORLD)

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        event = self.game.event.active_event
        default_font = self.default_font
        positive_font = self.positive_font
        warning_font = self.warning_font
        show_event_result = self.game.data.options["show_event_option_result"]
        state = self.game.event.state
        window_width = self.game.window.width
        window_height = self.game.window.height

        # positions
        start_x = 20
        start_y = 50

        # draw description
        current_x = start_x
        current_y = start_y
        frame_line_width = window_width - (current_x * 2)
        font_height = default_font.height
        max_height = ((window_height // 2) - current_y) - font_height
        frame = Frame(
            (current_x, current_y),
            text_and_font=(event["description"], default_font),
            max_line_width=frame_line_width,
            max_height=max_height,
        )
        self.elements["description"] = frame

        # move to half way down screen
        current_y = window_height // 2

        # draw separator
        offset = 80
        line_width = window_width - (offset * 2)
        surface = pygame.Surface((line_width, 1))
        pygame.draw.line(surface, (117, 50, 168), (0, 0), (line_width, 0))
        frame = Frame((offset, current_y), surface)
        self.elements["separator"] = frame

        # increment position
        current_y += 10

        panel_list = []
        panel_state = False
        if state == EventState.MAKE_DECISION:
            panel_state = True

            for counter, option in enumerate(event["options"]):
                # get option text
                if show_event_result:
                    option_text = option["text"] + " [" + option["displayed_result"] + "]"
                else:
                    option_text = option["text"]

                # build frame
                frame = Frame((current_x, current_y), text_and_font=(option_text, default_font), is_selectable=True)
                self.elements[f"option_{counter}"] = frame
                panel_list.append(frame)

                # increment position
                current_y += frame.height + GAP_SIZE

        # create panel
        panel = Panel(panel_list, panel_state)
        self.add_panel(panel, "options")

        panel_list = []
        panel_state = False
        if state == EventState.RESULT:
            panel_state = True

            # indent x
            current_x = window_width // 4

            # draw option chosen
            frame = Frame((current_x, current_y), text_and_font=(self.selected_option, default_font))
            self.elements["selected_option"] = frame

            # increment position
            current_y += frame.height + (GAP_SIZE * 2)

            # centre results
            current_x = (window_width // 2) - (DEFAULT_IMAGE_SIZE // 2)

            # draw results
            results = self.game.event.triggered_results
            for counter, result in enumerate(results):
                key, value, target = self.game.event.parse_result(result)

                # only show results we want the player to be aware of
                if key in ["unlock_event"]:
                    continue

                # get image
                result_image = self._get_result_image(key)

                # get font
                if int(value) > 0:
                    # more injuries is bad, unlike other resources
                    if key not in ["injury"]:
                        font = positive_font
                    else:
                        font = warning_font
                else:
                    # less injuries is good, unlike other resources
                    if key in ["injury"]:
                        font = positive_font
                    else:
                        font = warning_font

                frame = Frame(
                    (
                        current_x,
                        current_y,
                    ),
                    result_image,
                    text_and_font=(value, font),
                    is_selectable=False,
                )
                self.elements[f"result_{counter}"] = frame
                panel_list.append(frame)

                # increment position
                current_y += frame.height + GAP_SIZE

            # only draw exit button once decision made
            self.add_exit_button()

        # create panel
        panel = Panel(panel_list, panel_state)
        self.add_panel(panel, "results")

        self.rebuild_resource_elements()

    def handle_options_input(self):
        options = self.game.event.active_event["options"]

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            index = self.current_panel.selected_index
            logging.info(f"Selected option {index}, {options[index]}.")

            # save results for later
            self.game.event.triggered_results = options[index]["result"]
            self.selected_option = options[index]["text"]

            # trigger results and update display
            self.game.event.trigger_result()
            self.game.event.state = EventState.RESULT
            self.rebuild_ui()

            self.select_panel("exit")

    def _get_result_image(self, result_key: str) -> pygame.Surface:
        """
        Get an image for the result key given.
        """
        icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        if result_key == "gold":
            image = self.game.assets.get_image("stats", "gold", icon_size)

        elif result_key == "rations":
            image = self.game.assets.get_image("stats", "rations", icon_size)

        elif result_key == "morale":
            image = self.game.assets.get_image("stats", "morale", icon_size)

        elif result_key == "charisma":
            image = self.game.assets.get_image("stats", "charisma", icon_size)

        elif result_key == "leadership":
            image = self.game.assets.get_image("stats", "leadership", icon_size)

        elif result_key == "injury":
            image = self.game.assets.get_image("stats", "injury", icon_size)

        else:
            logging.warning(f"Result key not recognised. Image not found used.")
            image = self.game.assets.get_image("debug", "not_found", icon_size)

        return image

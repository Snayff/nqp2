from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, EventState, FontEffects, FontType, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game
    from scripts.scenes.event.scene import EventScene

__all__ = ["EventUI"]


class EventUI(UI):
    """
    Represent the UI of the EventScene.
    """

    def __init__(self, game: Game, parent_scene: EventScene):
        super().__init__(game, True)
        self._parent_scene: EventScene = parent_scene

        self._selected_option: str = ""  # the option selected

        self.set_instruction_text("Choose what to do next.")

    def update(self, delta_time: float):
        super().update(delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # selection in panel
        if self._game.input.states["down"]:
            self._current_panel.select_next_element()

        if self._game.input.states["up"]:
            self._current_panel.select_previous_element()

        # view troupe
        if self._game.input.states["view_troupe"]:
            self._game.change_scene([SceneType.VIEW_TROUPE])

        # panel specific input
        if self._current_panel == self._panels["options"]:
            self._handle_options_input()

        elif self._current_panel == self._panels["exit"]:

            if self._game.input.states["select"]:
                self._game.deactivate_scene(SceneType.EVENT)

                self._game.event.state = EventState.MAKE_DECISION

    def render(self, surface: pygame.surface):
        # show core info
        self._draw_instruction(surface)

        # draw elements
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        # positions
        start_x = 18
        start_y = 50

        # values needed for multiple elements
        event = self._game.event.active_event
        show_event_result = self._game.data.options["show_event_option_result"]
        state = self._game.event.state
        window_width = self._game.window.width
        window_height = self._game.window.height
        create_font = self._game.assets.create_font
        frame_line_width = window_width - (start_x * 2)

        # draw background
        bg_surface = pygame.Surface((frame_line_width, window_height - (start_y * 2)), SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        frame = Frame((start_x, start_y), image=bg_surface, is_selectable=False)
        self._elements[f"background"] = frame

        # draw description
        current_x = start_x + 2
        current_y = start_y
        fancy_font = self._game.assets.create_fancy_font(event["description"], font_effects=[FontEffects.FADE_IN])
        font_height = fancy_font.line_height
        max_height = ((window_height // 2) - current_y) - font_height
        frame = Frame(
            (current_x, current_y),
            font=fancy_font,
            max_height=max_height,
            max_width=frame_line_width,
            is_selectable=False,
        )
        self._elements["description"] = frame

        # move to half way down screen
        current_y = window_height // 2

        # draw separator
        offset = 80
        line_width = window_width - (offset * 2)
        surface = pygame.Surface((line_width, 1))
        pygame.draw.line(surface, (117, 50, 168), (0, 0), (line_width, 0))
        frame = Frame((offset, current_y), surface)
        self._elements["separator"] = frame

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
                frame = Frame(
                    (current_x, current_y), font=create_font(FontType.DEFAULT, option_text), is_selectable=True
                )
                self._elements[f"option_{counter}"] = frame
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
            frame = Frame(
                (current_x, current_y), font=create_font(FontType.DEFAULT, self._selected_option), is_selectable=True
            )
            self._elements["selected_option"] = frame

            # increment position
            current_y += frame.height + (GAP_SIZE * 2)

            # centre results
            current_x = (window_width // 2) - (DEFAULT_IMAGE_SIZE // 2)

            # draw results
            results = self._game.event.triggered_results
            for counter, result in enumerate(results):
                key, value, target = self._game.event.parse_event_string(result)

                # only show results we want the player to be aware of
                if key in ["unlock_event"]:
                    continue

                # get image
                result_image = self._get_result_image(key, value, target)

                # get font
                try:
                    if int(value) > 0:
                        # more injuries is bad, unlike other resources
                        if key not in ["injury"]:
                            font_type = FontType.POSITIVE
                        else:
                            font_type = FontType.NEGATIVE
                    else:
                        # less injuries is good, unlike other resources
                        if key in ["injury"]:
                            font_type = FontType.POSITIVE
                        else:
                            font_type = FontType.NEGATIVE

                    # we know its a number, so take as value
                    text = value
                except ValueError:
                    # string could not be converted to int
                    font_type = FontType.POSITIVE

                    # generic message to handle adding units
                    text = "recruited."

                # create the frame
                frame = Frame(
                    (current_x, current_y), image=result_image, font=create_font(font_type, text), is_selectable=False
                )
                self._elements[f"result_{counter}"] = frame
                panel_list.append(frame)

                # increment position
                current_y += frame.height + GAP_SIZE

            # only draw exit button once decision made
            self.add_exit_button()

        # create panel
        panel = Panel(panel_list, panel_state)
        self.add_panel(panel, "results")

        self.rebuild_resource_elements()

    def _handle_options_input(self):
        options = self._game.event.active_event["options"]

        # select option and trigger result
        if self._game.input.states["select"]:
            self._game.input.states["select"] = False

            index = self._current_panel.selected_index
            logging.info(f"Selected option {index}, {options[index]}.")

            # save results for later
            self._game.event.triggered_results = options[index]["result"]
            self._selected_option = options[index]["text"]

            # trigger results and update display
            self._game.event._trigger_result()
            self._game.event.state = EventState.RESULT
            self.rebuild_ui()

            self.select_panel("exit")

    def _get_result_image(self, result_key: str, result_value: str, result_target: str) -> pygame.Surface:
        """
        Get an image for the result key given.
        """
        icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        if result_key == "gold":
            image = self._game.assets.get_image("stats", "gold", icon_size)

        elif result_key == "rations":
            image = self._game.assets.get_image("stats", "rations", icon_size)

        elif result_key == "morale":
            image = self._game.assets.get_image("stats", "morale", icon_size)

        elif result_key == "charisma":
            image = self._game.assets.get_image("stats", "charisma", icon_size)

        elif result_key == "leadership":
            image = self._game.assets.get_image("stats", "leadership", icon_size)

        elif result_key == "injury":
            image = self._game.assets.get_image("stats", "injury", icon_size)

        elif result_key == "add_unit_resource":
            unit = self._game.event.event_resources[result_value]
            unit_type = unit.type
            image = self._game.assets.unit_animations[unit_type]["icon"][0]

        elif result_key == "add_specific_unit":
            image = self._game.assets.unit_animations[result_value]["icon"][0]

        else:
            logging.warning(f"Result key not recognised. Image not found used.")
            image = self._game.assets.get_image("debug", "not_found", icon_size)

        return image

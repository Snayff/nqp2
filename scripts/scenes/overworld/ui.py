from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import Direction, NodeType, OverworldState, SceneType
from scripts.ui_elements.frame import Frame

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["OverworldUI"]


############# TO DO LIST ##################


class OverworldUI(UI):
    """
    Represents the overworld UI.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        # N.B. Doesnt use Panels to handle input.

        self.set_instruction_text(
            "Choose where you will go next. Up/Down for moving between rings and Left/Right for clockwise "
            "and anti-clockwise."
        )

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.game.overworld.state == OverworldState.READY:

            node_container = self.game.overworld.node_container

            if self.game.input.states["left"]:
                self.game.input.states["left"] = False
                node_container.select_next_node(Direction.LEFT)
                node_container.roll_for_event()

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False
                node_container.select_next_node(Direction.RIGHT)
                node_container.roll_for_event()

            if self.game.input.states["up"]:
                self.game.input.states["up"] = False
                node_container.select_next_node(Direction.UP)
                node_container.roll_for_event()

            if self.game.input.states["down"]:
                self.game.input.states["down"] = False
                node_container.select_next_node(Direction.DOWN)
                node_container.roll_for_event()

            if self.game.input.states["view_troupe"]:
                self.game.input.states["view_troupe"] = False
                self.game.change_scene(SceneType.VIEW_TROUPE)

            if self.game.input.states["select"]:
                self.game.input.states["select"] = False
                if not node_container.selected_node.is_complete:
                    node_container.trigger_current_node()

            # trigger event notification message
            node_container = self.game.overworld.node_container
            if node_container.show_event_notification:
                if node_container.event_notification_timer > 0:
                    self.elements["event_notification"].is_active = True
                    node_container.event_notification_timer -= delta_time
                else:
                    self.elements["event_notification"].is_active = False
                    node_container.show_event_notification = False

                    self.game.change_scene(SceneType.EVENT)

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        overworld_map = self.game.overworld
        warning_font = self.warning_font
        notification_font = self.notification_font

        if overworld_map.state == OverworldState.LOADING:
            # draw loading screen
            current_x = 10
            current_y = self.game.window.height - 20
            frame = Frame(
                (current_x, current_y),
                text_and_font=("Loading...", warning_font),
                is_selectable=False,
            )
            self.elements["loading_message"] = frame

        else:
            # N.B.  most drawing happens in the node_container

            # draw resources
            self.rebuild_resource_elements()

            # draw event notification
            notification = "Something is afoot!"
            current_x = 10
            current_y = int(self.game.window.height / 2)
            frame = Frame(
                (current_x, current_y),
                text_and_font=(notification, notification_font),
                is_selectable=False,
            )
            frame.is_active = False
            self.elements["event_notification"] = frame

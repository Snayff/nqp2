from __future__ import annotations

import logging

import pygame

from scripts.core.constants import SceneType
from scripts.ui_elements.input_box import InputBox

__all__ = ["DevConsole"]


class DevConsole(InputBox):
    def __init__(self, game):
        size = (100, 30)
        pos = (10, 10)
        super().__init__(game, size, pos)

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.focused:

            # pressed enter
            if self.game.input.states["typing_enter"]:
                self.game.input.states["typing_enter"] = False

                self._handle_dev_command()

                self.game.debug.toggle_dev_console_visibility()

    def render(self, surface: pygame.surface, offset=(0, 0)):
        super().render(surface)

    def _handle_dev_command(self):
        """
        Handle the command in the dev console. Expected format is "[command] [value]".
        """
        command = self.text
        confirmation_message = ""

        if command[:5] == "event":
            event_id = command[6:]  # +1 position to account for space

            # check active scene
            if self.game.active_scene.type not in (SceneType.MAIN_MENU, SceneType.RUN_SETUP):
                confirmation_message = self._switch_to_event(event_id)

        elif command[:8] == "god_mode":
            state = command[9:]  # +1 position to account for space

            # check active scene
            if self.game.active_scene.type not in (SceneType.MAIN_MENU, SceneType.RUN_SETUP):
                confirmation_message = self._toggle_god_mode(state)

        elif command[39:] == "create_unit_json_for_each_asset_folders":
            # check active scene
            if self.game.active_scene.type in (SceneType.MAIN_MENU):
                confirmation_message = self._add_unit_json_for_each_asset_folder()

        # update result
        if confirmation_message != "":
            self.game.active_scene.ui.set_instruction_text(confirmation_message, True)

    def _add_unit_json_for_each_asset_folder(self) -> str:
        pass

    def _toggle_god_mode(self, state: str) -> str:
        """
        Expects 'on' or 'off'.
        """
        if state == "on":
            self.game.memory.flags.append("god_mode")

            # add cheat flag
            if "cheated" not in self.game.memory.flags:
                self.game.memory.flags.append("cheated")
        elif state == "off":
            self.game.memory.flags.remove("god_mode")

        else:
            return ""  # exit early

        confirmation_message = f"God mode turned {state}."

        return confirmation_message

    def _switch_to_event(self, event_id: str) -> str:
        """
        Change the scene and load a specific event.
        """
        # validate event
        if event_id in self.game.memory.event_deck.keys():
            # load event
            self.game.event.load_event(event_id)
            self.game.event.ui.rebuild_ui()
            self.game.active_scene = self.game.event

            confirmation_message = f"Loaded event {event_id}."
            return confirmation_message

        else:
            logging.warning(f"DevConsole: {event_id} not found.")



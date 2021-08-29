from __future__ import annotations

import json
import logging
import os

import pygame

from scripts.core.constants import ASSET_PATH, DATA_PATH, SceneType
from scripts.core.utility import scene_to_scene_type
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

        elif command[:7] == "godmode":
            # check active scene
            if self.game.active_scene.type not in (SceneType.MAIN_MENU, SceneType.RUN_SETUP):
                confirmation_message = self._toggle_god_mode()

        elif command[:17] == "create_unit_jsons":
            # check active scene
            if self.game.active_scene.type in (SceneType.MAIN_MENU,):
                confirmation_message = self._add_unit_json_for_each_asset_folder()

        elif command[:] == "gallery":
            # check active scene
            if self.game.active_scene.type in (SceneType.MAIN_MENU,):
                confirmation_message = self._switch_to_gallery()

                # update result
        if confirmation_message != "":
            self.game.active_scene.ui.set_instruction_text(confirmation_message, True)

    def _add_unit_json_for_each_asset_folder(self) -> str:
        """
        Add a placeholder unit_json for every unit asset folder.
        """
        count = 0
        unit_dict = list(self.game.data.units.values())[0]

        logging.debug(f"Creating unit jsons...")

        for unit_name in os.listdir(ASSET_PATH / "units"):
            unit_data_path = DATA_PATH / "units" / unit_name

            # skip system files and templates
            if unit_name[1:] == "_":
                continue

            # check if json already exists
            if os.path.isfile(f"{unit_data_path}.json"):
                continue

            # it doesnt exist, create the json
            unit_dict["type"] = unit_name
            with open(f"{unit_data_path}.json", "w") as file:
                json.dump(unit_dict, file, indent=4)
                logging.debug(f"-> Created {unit_name} json.")

            count += 1

        if count > 0:
            confirmation_message = f"{count} unit jsons created."
        else:
            confirmation_message = ""

        logging.debug(f"All required unit jsons created. {count} created.")

        return confirmation_message

    def _toggle_god_mode(self) -> str:
        """
        Turns god_mode on or off.
        """
        if "godmode" in self.game.memory.flags:
            self.game.memory.flags.remove("godmode")
            state = "off"

        else:
            self.game.memory.flags.append("godmode")

            state = "on"

            # add cheat flag
            if "cheated" not in self.game.memory.flags:
                self.game.memory.flags.append("cheated")


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

    def _switch_to_gallery(self) -> str:
        self.game.dev_gallery.previous_scene_type = scene_to_scene_type(self.game.active_scene)
        self.game.dev_gallery.ui.rebuild_ui()
        self.game.active_scene = self.game.dev_gallery

        confirmation_message = f"Loaded gallery."
        return confirmation_message


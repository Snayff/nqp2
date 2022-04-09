from __future__ import annotations

import csv
import logging
import os

import pygame
import yaml

from nqp.core.constants import ASSET_PATH, DATA_PATH, SceneType, WorldState
from nqp.core.utility import scene_to_scene_type
from nqp.ui_elements.generic.ui_input_box import UIInputBox

__all__ = ["DevConsole"]


class DevConsole(UIInputBox):
    def __init__(self, game):
        size = (100, 30)
        pos = (10, 10)
        super().__init__(game, size, pos)

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.focused:

            # pressed enter
            if self._game.input.states["typing_enter"]:
                self._game.input.states["typing_enter"] = False

                self._handle_dev_command()

                self._game.debug.toggle_dev_console_visibility()

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        super().draw(surface)

    def _handle_dev_command(self):
        """
        Handle the command in the dev console. Expected format is "[command] [value]".
        """
        command = self.font.text
        confirmation_message = ""

        if command[:5] == "event":
            event_id = command[6:]  # +1 position to account for space

            # check active scene
            if (SceneType.MAIN_MENU, SceneType.RUN_SETUP) not in self._game.scene_stack:
                confirmation_message = self._switch_to_event(event_id)

        elif command[:7] == "godmode":
            # check active scene
            if SceneType.WORLD in self._game.scene_stack:
                confirmation_message = self._toggle_godmode()

        elif command[:17] == "create_unit_data":
            # check active scene
            if SceneType.MAIN_MENU in self._game.scene_stack:
                confirmation_message = self._add_unit_data_for_each_asset_folder()

        elif command[:13] == "load_unit_csv":
            # check active scene
            if SceneType.MAIN_MENU in self._game.scene_stack:
                confirmation_message = self._load_unit_csv()

        elif command[:7] == "gallery":
            # check active scene
            if SceneType.MAIN_MENU in self._game.scene_stack:
                confirmation_message = self._switch_to_gallery()

        elif command[:11] == "data_editor":
            # check active scene
            if SceneType.MAIN_MENU in self._game.scene_stack:
                confirmation_message = self._switch_to_data_editor()

        elif command[:13] == "combat_result":
            result = command[14:]  # +1 position to account for space

            # check active scene
            if SceneType.WORLD in self._game.scene_stack and self._game.world.state == WorldState.COMBAT:
                confirmation_message = self._process_combat_result(result)

        # update result
        if confirmation_message != "":
            active_scene = self._game.scene_stack[0]
            active_scene.ui.set_instruction_text(confirmation_message, True)

    def _add_unit_data_for_each_asset_folder(self) -> str:
        """
        Add a placeholder unit data for every unit asset folder.
        """
        count = 0
        unit_dict = list(self._game.data.units.values())[0]

        logging.debug(f"Creating unit data...")

        for unit_name in os.listdir(ASSET_PATH / "units"):
            unit_data_path = DATA_PATH / "units" / unit_name

            # skip system files and templates
            if unit_name[1:] == "_":
                continue

            # check if data already exists
            if os.path.isfile(f"{unit_data_path}.yaml"):
                continue

            # it doesnt exist, create the data
            unit_dict["type"] = unit_name
            with open(f"{unit_data_path}.yaml", "w") as file:
                yaml.dump(unit_dict, file, Dumper=yaml.SafeDumper)
                logging.debug(f"-> Created {unit_name} yaml.")

            count += 1

        if count > 0:
            confirmation_message = f"{count} unit data created."
        else:
            confirmation_message = ""

        logging.debug(f"All required unit data created. {count} created.")

        return confirmation_message

    def _toggle_godmode(self) -> str:
        """
        Turns godmode on or off.
        """
        if "godmode" in self._game.memory.flags:
            self._game.memory.flags.remove("godmode")
            state = "off"

            logging.debug(f"Turned godmode off.")

        else:
            self._game.memory.flags.append("godmode")

            state = "on"

            logging.debug(f"Turned godmode on.")

            # add cheat flag
            if "cheated" not in self._game.memory.flags:
                self._game.memory.flags.append("cheated")

        confirmation_message = f"God mode turned {state}."

        return confirmation_message

    def _switch_to_event(self, event_id: str) -> str:
        """
        Change the scene and load a specific event.
        """
        # validate event
        if event_id in self._game.memory.event_deck.keys():
            # load event
            self._game.event.load_event(event_id)
            self._game.event.ui.rebuild_ui()
            self._game.active_scene = self._game.event

            confirmation_message = f"Loaded event {event_id}."
            return confirmation_message

        else:
            logging.warning(f"DevConsole: {event_id} not found.")

    def _switch_to_gallery(self) -> str:
        self._game.dev_gallery.previous_scene_type = scene_to_scene_type(self._game.active_scene)
        self._game.dev_gallery.ui.rebuild_ui()
        self._game.active_scene = self._game.dev_gallery

        confirmation_message = f"Loaded gallery."
        return confirmation_message

    def _switch_to_data_editor(self):
        self._game.dev_unit_data.previous_scene_type = scene_to_scene_type(self._game.active_scene)
        self._game.dev_unit_data.ui.rebuild_ui()
        self._game.active_scene = self._game.dev_unit_data

        confirmation_message = f"Loaded data editor."
        return confirmation_message

    def _load_unit_csv(self):
        """
        Load the unit csv into the unit data files.
        """
        existing_units = list(self._game.data.units.keys())
        num_updated = 0
        num_created = 0

        logging.debug(f"Loading unit csv...")

        # load the data
        with open("units.csv", "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                str_path = str(DATA_PATH / "units" / f"{row['type']}.yaml")

                # check if unit file already exists
                if row["type"] in existing_units:

                    # open existing data
                    with open(str_path, "r") as unit_data:
                        data = yaml.load(unit_data, Loader=yaml.SafeLoader)

                        # update data
                        data["health"] = int(row["health"])
                        data["defence"] = int(row["defence"])
                        data["attack"] = int(row["attack"])
                        data["range"] = int(row["range"])
                        data["attack_speed"] = float(row["attack_speed"])
                        data["move_speed"] = int(row["move_speed"])
                        data["ammo"] = int(row["ammo"])
                        data["count"] = int(row["count"])
                        data["tier"] = int(row["tier"])
                        data["faction"] = row["faction"]
                        data["default_behaviour"] = row["default_behaviour"]

                    # delete previous file
                    os.remove(str_path)

                    # create new file
                    with open(str_path, "w") as unit_data:
                        yaml.dump(data, unit_data, Dumper=yaml.SafeDumper)

                    num_updated += 1

                else:
                    data = row.copy()

                    # add needed values not held in csv
                    data["size"] = 1
                    data["weight"] = 2
                    data["gold_cost"] = 0

                    # create new file
                    with open(str_path, "w") as unit_data:
                        yaml.dump(data, unit_data, Dumper=yaml.SafeDumper)

                    num_created += 1

        confirmation_message = f"Updated {num_updated} unit details and created {num_created} units."

        logging.debug(f"->{confirmation_message})")

        return confirmation_message

    def _process_combat_result(self, result: str) -> str:
        """
        Set the result of the current combat. Result should be 'win' or 'lose'.
        """
        if result == "win":
            logging.debug(f"Skipped to combat victory.")
            self._game.combat.end_combat()
            self._game.combat.process_victory()
            confirmation_message = "Combat won."

        elif result == "lose":
            logging.debug(f"Skipped to combat defeat.")
            self._game.combat.end_combat()
            self._game.combat.process_defeat()
            confirmation_message = "Combat lost."

        else:
            confirmation_message = f"Result type ({result}) not recognised."

        return confirmation_message

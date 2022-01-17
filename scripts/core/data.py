from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, TYPE_CHECKING, Union

from scripts.core.constants import DATA_PATH
from scripts.scenes.combat.elements.behavior_manager import BehaviourManager

if TYPE_CHECKING:
    from typing import Dict, List

    from scripts.core.game import Game

__all__ = ["Data"]


class Data:
    """
    Raw data that doesnt change. Usually pulled from external files.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self._game: Game = game

        self.commanders: Dict[str, Any] = self._load_commanders()
        self.units: Dict[str, Any] = self._load_unit_info()
        self.behaviours = BehaviourManager()
        self.tiles = self._load_tile_info()
        self.factions: List[str] = self._create_homes_list()
        self.events: Dict[str, Any] = self._load_events()
        self.upgrades: Dict[str, Any] = self._load_upgrades()
        self.combats: Dict[str, Any] = self._load_combats()
        self.bosses: Dict[str, Any] = self._load_bosses()
        self.skills: Dict[str, Any] = self._load_skills()

        self.config: Dict[str, Any] = self._load_config()
        self.options: Dict[str, Any] = self._load_options()

        # record duration
        end_time = time.time()
        logging.debug(f"Data: initialised in {format(end_time - start_time, '.2f')}s.")

    @staticmethod
    def _load_tile_info() -> Dict:
        f = open(str(DATA_PATH / "maps" / "tiles.json"), "r")
        tile_info_raw = json.load(f)
        f.close()

        # convert tile IDs to tuples (JSON doesn't allow tuples)
        tile_info = {}
        for tile_id in tile_info_raw:
            tile_info[
                tuple([id_section if i == 0 else int(id_section) for i, id_section in enumerate(tile_id.split("|"))])
            ] = tile_info_raw[tile_id]

        logging.debug(f"Data: All tileset data loaded.")

        return tile_info

    @staticmethod
    def _load_unit_info() -> Dict:
        units = {}
        for unit in os.listdir("data/units"):
            f = open(str(DATA_PATH / "units" / unit), "r")
            data = json.load(f)
            units[data["type"]] = data
            f.close()

        logging.debug(f"Data: All unit data loaded.")

        return units

    def _create_homes_list(self) -> List[str]:
        factions = []

        for unit in self.units.values():
            if unit["faction"] not in factions:
                factions.append(unit["faction"])

        return factions

    @staticmethod
    def _load_upgrades() -> Dict:
        upgrades = {}
        for upgrade in os.listdir("data/upgrades"):
            f = open(str(DATA_PATH / "upgrades" / upgrade), "r")
            data = json.load(f)
            upgrades[data["type"]] = data
            f.close()

        logging.debug(f"Data: All upgrade data loaded.")

        return upgrades

    @staticmethod
    def _load_events() -> Dict:
        events = {}
        for event in os.listdir("data/events"):
            f = open(str(DATA_PATH / "events" / event), "r")
            data = json.load(f)
            events[data["type"]] = data
            f.close()

        logging.debug(f"Data: All event data loaded.")

        return events

    @staticmethod
    def _load_config() -> Dict:
        f = open(str(DATA_PATH / "config.json"), "r")
        config = json.load(f)
        f.close()

        logging.debug(f"Data: Config data loaded.")

        return config

    @staticmethod
    def _load_commanders() -> Dict:
        commanders = {}
        for commander in os.listdir("data/commanders"):
            f = open(str(DATA_PATH / "commanders" / commander), "r")
            data = json.load(f)
            commanders[data["type"]] = data
            f.close()

        logging.debug(f"Data: All commanders data loaded.")

        return commanders

    @staticmethod
    def _load_bosses() -> Dict:
        bosses = {}
        for commander in os.listdir("data/bosses"):
            f = open(str(DATA_PATH / "bosses" / commander), "r")
            data = json.load(f)
            bosses[data["type"]] = data
            f.close()

        logging.debug(f"Data: All bosses data loaded.")

        return bosses

    @staticmethod
    def _load_combats():
        combats = {}
        for combat in os.listdir("data/combats"):
            f = open(str(DATA_PATH / "combats" / combat), "r")
            data = json.load(f)
            combats[data["type"]] = data
            f.close()

        logging.debug(f"Data: All combats data loaded.")

        return combats

    @staticmethod
    def _load_skills():
        skills = {}
        for skill in os.listdir("data/skills"):
            f = open(str(DATA_PATH / "skills" / skill), "r")
            data = json.load(f)
            skills[skill.split(".")[0]] = data
            f.close()

        logging.debug(f"Data: All skills data loaded.")

        return skills

    @staticmethod
    def _load_options():
        f = open(str(DATA_PATH / "options.json"), "r")
        config = json.load(f)
        f.close()

        logging.debug(f"Data: Options data loaded.")

        return config

    def get_units_by_category(self, factions: List[str], tiers: List[int] = None) -> List[str]:
        """
        Return list of unit types for all units with a matching faction and tier.
        """
        # handle mutable default
        if tiers is None:
            tiers = [1, 2, 3, 4]
        units = []

        for faction in factions:
            # check faction is valid
            if faction not in self.factions:
                logging.warning(f"get_units_by_category: {faction} not found in {self.factions}. Value skipped.")
                continue

            # get units as specified
            for unit in self.units.values():
                if unit["faction"] == faction and unit["tier"] in tiers:
                    units.append(unit["type"])

        return units

    def get_unit_occur_rate(self, unit_type: str) -> int:
        """
        Get the unit occur rate based on the tier. Lower means less often.
        """
        tier_occur_rates = self.config["unit_tier_occur_rates"]
        unit_details = self.units[unit_type]
        unit_tier = unit_details["tier"]

        occur_rate = tier_occur_rates[str(unit_tier)]  # str as json keys are strs

        return occur_rate

    def get_event_occur_rate(self, id_: str) -> int:
        """
        Get the event occur rate based on the tier. Lower means less often.
        """
        tier_occur_rates = self.config["event_tier_occur_rates"]
        event = self.events[id_]
        event_tier = event["tier"]

        occur_rate = tier_occur_rates[str(event_tier)]  # str as json keys are strs

        return occur_rate

    def get_combat_occur_rate(self, id_: str) -> int:
        """
        Get the combat occur rate based on the tier. Lower means less often.
        """
        tier_occur_rates = self.config["combat_tier_occur_rates"]
        combat = self.combats[id_]
        combat_tier = combat["tier"]

        occur_rate = tier_occur_rates[str(combat_tier)]  # str as json keys are strs

        return occur_rate

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING, Union

import yaml

from scripts.core.constants import DATA_PATH
from scripts.scene_elements.behavior_manager import BehaviourManager

if TYPE_CHECKING:
    from typing import Dict, List

    from scripts.core.game import Game
    from scripts.scene_elements.item import ItemData

__all__ = ["Data"]


def load_yaml(path: Union[str, Path]) -> Any:
    """
    Load YAML data with the SafeLoader

    """
    with open(str(path), "r") as fp:
        data = yaml.load(fp, Loader=yaml.SafeLoader)
    return data


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
        self.behaviours = BehaviourManager()  # TODO - this isnt data and should be elsewhere
        self.tiles = self._load_tile_info()  # TODO - can we get rid of this?
        self.factions: List[str] = self._create_homes_list()
        self.events: Dict[str, Any] = self._load_events()
        self.upgrades: Dict[str, Any] = self._load_upgrades()
        self.combats: Dict[str, Any] = self._load_combats()
        self.bosses: Dict[str, Any] = self._load_bosses()
        self.skills: Dict[str, Any] = self._load_skills()
        self.items: Dict[str, ItemData] = self._load_items()

        self.config: Dict[str, Any] = self._load_config()
        self.options: Dict[str, Any] = self._load_options()

        # record duration
        end_time = time.time()
        logging.debug(f"Data: initialised in {format(end_time - start_time, '.2f')}s.")

    @staticmethod
    def _load_tile_info() -> Dict:
        tile_info_raw = load_yaml(DATA_PATH / "maps" / "tiles.yaml")

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
            data = load_yaml(DATA_PATH / "units" / unit)
            units[data["type"]] = data

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
            data = load_yaml(DATA_PATH / "upgrades" / upgrade)
            upgrades[data["type"]] = data

        logging.debug(f"Data: All upgrade data loaded.")

        return upgrades

    @staticmethod
    def _load_events() -> Dict:
        events = {}
        for event in os.listdir("data/events"):
            data = load_yaml(DATA_PATH / "events" / event)
            events[data["type"]] = data

        logging.debug(f"Data: All event data loaded.")

        return events

    @staticmethod
    def _load_config() -> Dict:
        config = load_yaml(DATA_PATH / "config.yaml")
        logging.debug(f"Data: Config data loaded.")

        return config

    @staticmethod
    def _load_commanders() -> Dict:
        commanders = {}
        for commander in os.listdir("data/commanders"):
            data = load_yaml(DATA_PATH / "commanders" / commander)
            commanders[data["type"]] = data

        logging.debug(f"Data: All commanders data loaded.")

        return commanders

    @staticmethod
    def _load_bosses() -> Dict:
        bosses = {}
        for commander in os.listdir("data/bosses"):
            data = load_yaml(DATA_PATH / "bosses" / commander)
            bosses[data["type"]] = data

        logging.debug(f"Data: All bosses data loaded.")

        return bosses

    @staticmethod
    def _load_combats():
        combats = {}
        for combat in os.listdir("data/combats"):
            data = load_yaml(DATA_PATH / "combats" / combat)
            combats[data["type"]] = data

        logging.debug(f"Data: All combats data loaded.")

        return combats

    @staticmethod
    def _load_skills():
        skills = {}
        for skill in os.listdir("data/skills"):
            data = DATA_PATH / "skills" / skill
            skills[skill.split(".")[0]] = data

        logging.debug(f"Data: All skills data loaded.")

        return skills

    @staticmethod
    def _load_options():
        config = load_yaml(DATA_PATH / "options.yaml")
        logging.debug(f"Data: Options data loaded.")

        return config

    @staticmethod
    def _load_items() -> Dict[str:ItemData]:
        from scripts.scene_elements.item import ItemData

        items = {}
        for filename in os.listdir("data/items"):
            with open(str(DATA_PATH / "items" / filename), "r") as fp:
                data = yaml.load(fp, Loader=yaml.SafeLoader)
                item_data = ItemData(**data)
                items[filename.split(".")[0]] = item_data

        logging.debug(f"Data: All items data loaded.")

        return items

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

        # data is stored as yaml, so convert ints to str for serialization
        occur_rate = tier_occur_rates[str(unit_tier)]

        return occur_rate

    def get_event_occur_rate(self, id_: str) -> int:
        """
        Get the event occur rate based on the tier. Lower means less often.
        """
        tier_occur_rates = self.config["event_tier_occur_rates"]
        event = self.events[id_]
        event_tier = event["tier"]

        # data is stored as yaml, so convert ints to str for serialization
        occur_rate = tier_occur_rates[str(event_tier)]

        return occur_rate

    def get_combat_occur_rate(self, id_: str) -> int:
        """
        Get the combat occur rate based on the tier. Lower means less often.
        """
        tier_occur_rates = self.config["combat_tier_occur_rates"]
        combat = self.combats[id_]
        combat_tier = combat["tier"]

        # data is stored as yaml, so convert ints to str for serialization
        occur_rate = tier_occur_rates[str(combat_tier)]

        return occur_rate

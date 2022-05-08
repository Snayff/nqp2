from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING, Union

import snecs
import yaml

from nqp.core.constants import DATA_PATH
from nqp.core.debug import Timer
from nqp.world_elements.item import Item

if TYPE_CHECKING:
    from typing import Dict, List

    from nqp.core.game import Game
    from nqp.world_elements.item import ItemData

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
        with Timer("Data: initialised"):
            self._game: Game = game

            self.effects: Dict[str:Any] = {}
            self.commanders: Dict[str, Any] = {}
            self.units: Dict[str, Any] = {}
            self.tiles = {}  # TODO - can we get rid of this?
            self.factions: List[str] = []
            self.events: Dict[str, Any] = {}
            self.upgrades: Dict[str, Any] = {}
            self.combats: Dict[str, Any] = {}
            self.bosses: Dict[str, Any] = {}
            self.skills: Dict[str, Any] = {}
            self.items: Dict[str, ItemData] = {}

            self.config: Dict[str, Any] = {}
            self.options: Dict[str, Any] = {}

            self.load_all_data()

    def load_all_data(self):
        """
        Reload all data
        """
        self.effects = self._load_effects()
        self.commanders = self._load_commanders()
        self.units = self._load_unit_info()
        self.factions = self._create_factions_list()  # must call after units
        self.tiles = self._load_tile_info()  # TODO - can we get rid of this?
        self.events = self._load_events()
        self.upgrades = self._load_upgrades()
        self.combats = self._load_combats()
        self.bosses = self._load_bosses()
        self.skills = self._load_skills()
        self.items = self._load_items()

        self.config = self._load_config()
        self.options = self._load_options()

    @staticmethod
    def _load_tile_info() -> Dict:
        tile_info_raw = load_yaml(DATA_PATH / "maps" / "tiles.yaml")

        # convert tile IDs to tuples (JSON doesn't allow tuples)
        tile_info = {}
        counter = 0
        for tile_id in tile_info_raw:
            tile_info[
                tuple([id_section if i == 0 else int(id_section) for i, id_section in enumerate(tile_id.split("|"))])
            ] = tile_info_raw[tile_id]
            counter += 1

        logging.debug(f"Data: {counter} tilesets loaded.")

        return tile_info

    @staticmethod
    def _load_unit_info() -> Dict:
        units = {}
        counter = 0
        for unit in os.listdir("data/units"):
            data = load_yaml(DATA_PATH / "units" / unit)
            units[data["type"]] = data

            counter += 1

        logging.debug(f"Data: {counter} units loaded.")

        return units

    def _create_factions_list(self) -> List[str]:
        """
        Create factions list from units data
        """
        factions = []

        for unit in self.units.values():
            if unit["faction"] not in factions:
                factions.append(unit["faction"])

        return factions

    @staticmethod
    def _load_upgrades() -> Dict:
        upgrades = {}
        counter = 0
        for upgrade in os.listdir("data/upgrades"):
            data = load_yaml(DATA_PATH / "upgrades" / upgrade)
            upgrades[data["type"]] = data

            counter += 1

        logging.debug(f"Data: {counter} upgrades loaded.")

        return upgrades

    @staticmethod
    def _load_events() -> Dict:
        events = {}
        counter = 0
        for event in os.listdir("data/events"):
            data = load_yaml(DATA_PATH / "events" / event)
            events[data["type"]] = data

            counter += 1

        logging.debug(f"Data: {counter} events loaded.")

        return events

    @staticmethod
    def _load_config() -> Dict:
        config = load_yaml(DATA_PATH / "config.yaml")
        logging.debug(f"Data: Config data loaded.")

        return config

    @staticmethod
    def _load_commanders() -> Dict:
        commanders = {}
        counter = 0
        for commander in os.listdir("data/commanders"):
            data = load_yaml(DATA_PATH / "commanders" / commander)
            commanders[data["type"]] = data

            counter += 1

        logging.debug(f"Data: {counter} commanders loaded.")

        return commanders

    @staticmethod
    def _load_bosses() -> Dict:
        bosses = {}
        counter = 0
        for commander in os.listdir("data/bosses"):
            data = load_yaml(DATA_PATH / "bosses" / commander)
            bosses[data["type"]] = data
            counter += 1

        logging.debug(f"Data: {counter} bosses loaded.")

        return bosses

    @staticmethod
    def _load_combats():
        combats = {}
        counter = 0
        for combat in os.listdir("data/combats"):
            data = load_yaml(DATA_PATH / "combats" / combat)
            combats[data["type"]] = data

            counter += 1

        logging.debug(f"Data: {counter} combats loaded.")

        return combats

    @staticmethod
    def _load_skills():
        skills = {}
        counter = 0
        for skill in os.listdir("data/skills"):
            data = DATA_PATH / "skills" / skill
            skills[skill.split(".")[0]] = data

            counter += 1

        logging.debug(f"Data: {counter} skills loaded.")

        return skills

    @staticmethod
    def _load_options():
        config = load_yaml(DATA_PATH / "options.yaml")
        logging.debug(f"Data: Options data loaded.")

        return config

    @staticmethod
    def _load_items() -> Dict[str:ItemData]:
        from nqp.world_elements.item import ItemData

        items = {}
        counter = 0
        for filename in os.listdir("data/items"):
            with open(str(DATA_PATH / "items" / filename), "r") as fp:
                data = yaml.load(fp, Loader=yaml.SafeLoader)
                item_data = ItemData(**data)
                items[filename.split(".")[0]] = item_data

                counter += 1

        logging.debug(f"Data: {counter} items loaded.")

        return items

    @staticmethod
    def _load_effects() -> Dict[str:Any]:
        # TODO: replace with autodiscover
        from nqp.effects.add_item import AddItemEffect
        from nqp.effects.stats_effect import StatsEffectSentinel
        from nqp.effects.sildreths_signature import SildrethsSignatureEffect

        effects = {
            "StatsEffect": StatsEffectSentinel,
            "AddItemEffect": AddItemEffect,
            "SildrethsSignatureEffect": SildrethsSignatureEffect,
        }
        logging.debug(f"Data: {len(effects)} items loaded.")

        # TODO: replace with autodiscover
        from nqp.core.effect import EffectProcessorComponent
        from nqp.effects.stats_effect import StatsEffectProcessor
        from nqp.effects.burn import OnFireStatusProcessor

        for processor_class in (
            StatsEffectProcessor,
            OnFireStatusProcessor,
        ):
            snecs.new_entity([EffectProcessorComponent(processor_class())])

        return effects

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

    def create_effect(self, data: Dict[str, Any], params: Dict[str:Any]):
        """
        Return Effect from data found in data files

        """
        name = data.pop("name")
        effect_class = self.effects[name]
        return effect_class.from_dict(data, params)

    def create_item(self, name: str):
        """
        Return Item by name

        Args:
            name: Short name, same as the item filename without extension

        Returns:
            New Item entity id

        """
        item_data = self.items[name]
        item = Item(
            name=item_data.name,
            is_signature=item_data.is_signature,
        )
        effects = [self.create_effect(data, item) for data in item_data.effects]
        components = [item] + effects
        entity = snecs.new_entity(components)
        return entity

from __future__ import annotations

import json
import logging
import os
import time
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.behavior_manager import BehaviourManager

if TYPE_CHECKING:
    from typing import Dict, List

    from scripts.core.game import Game

__all__ = ["Data"]


class Data:
    """
    Game related values that persist outside of individual “scenes”. E.g. money.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self.game: Game = game

        self.units: Dict = self.load_unit_info()
        self.behaviours = BehaviourManager()
        self.tiles = self.load_tile_info()


        # event
        self.events: Dict = self.load_events()

        # record duration
        end_time = time.time()
        logging.info(f"Data: initialised in {format(end_time - start_time, '.2f')}s.")

    @staticmethod
    def load_tile_info() -> Dict:
        f = open('data/tiles.json', 'r')
        tile_info_raw = json.load(f)
        f.close()

        # convert tile IDs to tuples (JSON doesn't allow tuples)
        tile_info = {}
        for tile_id in tile_info_raw:
            tile_info[tuple([id_section if i == 0 else int(id_section) for i, id_section in enumerate(tile_id.split('|'))])] = tile_info_raw[tile_id]

        logging.info(f"Data: All tileset data loaded.")

        return tile_info

    @staticmethod
    def load_unit_info() -> Dict:
        units = {}
        for unit in os.listdir("data/units"):
            f = open("data/units/" + unit, "r")
            units[unit.split(".")[0]] = json.load(f)
            f.close()

        logging.info(f"Data: All unit data loaded.")

        return units

    @staticmethod
    def load_events() -> Dict:
        events = {}
        for event in os.listdir("data/events"):
            f = open("data/events/" + event, "r")
            events[event.split(".")[0]] = json.load(f)
            f.close()

        logging.info(f"Data: All event data loaded.")

        return events

    def get_units_by_category(self, homes: List[str], tiers: List[int]):
        """
        Return list of unit types for all units with a matching home and tier.
        """
        units = []

        for home in homes:
            for unit in self.units.values():
                if unit["home"] == home and unit["tier"] in tiers:
                    units.append(unit["type"])



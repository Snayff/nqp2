from __future__ import annotations

import json
import logging
import os
import time
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.behavior_manager import BehaviorManager

if TYPE_CHECKING:
    from typing import Dict

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
        self.behaviors = BehaviorManager()

        # event
        self.events: Dict = self.load_events()


        # record duration
        end_time = time.time()
        logging.info(f"Data: initialised in {format(end_time - start_time, '.2f')}s.")

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

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from scripts.elements.behavior_manager import BehaviorManager
from scripts.elements.card_collection import CardCollection

if TYPE_CHECKING:
    from typing import Dict

    from scripts.management.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “scenes”. E.g. money.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        # combat
        self.deck: CardCollection = CardCollection(game)
        self.deck.generate(20)
        self.units: Dict = self.load_unit_info()
        self.behaviors = BehaviorManager()

        # event
        self.events: Dict = self.load_events()

        # general
        self.gold = 0

    @staticmethod
    def load_unit_info() -> Dict:
        units = {}
        for unit in os.listdir("data/units"):
            f = open("data/units/" + unit, "r")
            units[unit.split(".")[0]] = json.load(f)
            f.close()

        return units

    @staticmethod
    def load_events() -> Dict:
        events = {}
        for event in os.listdir("data/events"):
            f = open("data/events/" + event, "r")
            events[event.split(".")[0]] = json.load(f)
            f.close()

        return events

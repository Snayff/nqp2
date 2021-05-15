from __future__ import annotations

import os
import json
from typing import TYPE_CHECKING

from scripts.elements.card_collection import CardCollection
from scripts.elements.behavior_manager import BehaviorManager

if TYPE_CHECKING:
    from scripts.management.game import Game
    from typing import Dict

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “screens”. E.g. money.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.deck: CardCollection = CardCollection(game)
        self.deck.generate(20)

        self.units: Dict = self.load_unit_info()
        self.events: Dict = self.load_events()

        self.behaviors = BehaviorManager()

    @staticmethod
    def load_unit_info() -> Dict:
        units = {}
        for unit in os.listdir('data/units'):
            f = open('data/units/' + unit, 'r')
            units[unit.split('.')[0]] = json.load(f)
            f.close()

        return units

    @staticmethod
    def load_events() -> Dict:
        events = {}
        for event in os.listdir('data/events'):
            f = open('data/events/' + event, 'r')
            events[event.split('.')[0]] = json.load(f)
            f.close()

        return events

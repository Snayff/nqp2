from __future__ import annotations

import os
import json
from typing import TYPE_CHECKING

from scripts.elements.card_collection import CardCollection
from scripts.elements.behavior_manager import BehaviorManager

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “screens”. E.g. money.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.deck: CardCollection = CardCollection(game)
        self.deck.generate(20)

        self.unit_info = self.load_unit_info()

        self.behaviors = BehaviorManager()

    def load_unit_info(self):
        units = {}
        for unit in os.listdir('data/units'):
            f = open('data/units/' + unit, 'r')
            units[unit.split('.')[0]] = json.load(f)
            f.close()

        return units

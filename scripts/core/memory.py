from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.behavior_manager import BehaviorManager
from scripts.scenes.combat.elements.card import Card
from scripts.scenes.combat.elements.card_collection import CardCollection

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “scenes”. E.g. money.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        # combat
        self.unit_deck: CardCollection = CardCollection(game)
        self.unit_deck.generate_units(4)
        self.action_deck: CardCollection = CardCollection(game)
        self.action_deck.generate_actions(20)

        # FIXME - we need to differentiate between static data and dynamic data; units, behaviours etc. never change
        #  and should be held separately. e.g. split data and memory.
        self.units: Dict = self.load_unit_info()
        self.behaviors = BehaviorManager()

        # event
        self.events: Dict = self.load_events()

        # general
        self.gold = 10

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


    def amend_gold(self, amount: int):
        """
        Amend the current gold value by the given amount.
        """
        self.gold = max(0, self.gold + amount)

    def amend_unit(self, unit_name: str, amendment: str = "add"):
        """
        Amend the units. Amendment must be "add" or "remove".
        """
        if amendment == "add":
            self.unit_deck.add_card(Card(self.game, unit_name))
            # FIXME - this is adding to the CarcCollection but the card isnt showing up in Combat
        elif amendment == "remove":
            self.unit_deck.remove_card()
        else:
            # given incorrect command
            logging.warning(f"amend_unit: received {amendment} instead of add or remove. Ignored.")


from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.card import Card
from scripts.scenes.combat.elements.card_collection import CardCollection

if TYPE_CHECKING:
    pass

    from scripts.core.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “scenes”. E.g. money.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self.game: Game = game

        # combat
        self.troupe: Dict[Unit] = {}
        self.unit_deck: CardCollection = CardCollection(game)
        self.unit_deck.generate_units(4)
        self.action_deck: CardCollection = CardCollection(game)
        self.action_deck.generate_actions(20)

        # general
        self.gold = 10

        # record duration
        end_time = time.time()
        logging.info(f"Memory: initialised in {format(end_time - start_time, '.2f')}s.")

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
            # FIXME - this is adding to the CardCollection but the card isnt showing up in Combat
        elif amendment == "remove":
            self.unit_deck.remove_card()
        else:
            # given incorrect command
            logging.warning(f"amend_unit: received {amendment} instead of add or remove. Ignored.")

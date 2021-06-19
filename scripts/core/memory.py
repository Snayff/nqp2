from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.card_collection import CardCollection
from scripts.scenes.combat.elements.troupe import Troupe

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
        self._last_id = 0

        self.player_troupe: Troupe = Troupe(self.game, "player")
        self.player_troupe.debug_init_units()  # during testing only

        self.unit_deck: CardCollection = CardCollection(game)
        self.unit_deck.from_troupe(self.player_troupe)
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

    def generate_id(self) -> int:
        """
        Create unique ID for an instance, such as a unit.
        """
        self._last_id += 1
        return self._last_id

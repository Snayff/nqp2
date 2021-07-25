from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.card_collection import CardCollection
from scripts.scenes.combat.elements.commander import Commander
from scripts.scenes.combat.elements.troupe import Troupe

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

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

        # units
        self._last_id = 0

        # empty values will be overwritten in run_start
        self.player_troupe: Troupe = Troupe(self.game, "player", [])
        self.commander: Optional[Commander] = None

        self.unit_deck: CardCollection = CardCollection(game)
        self.unit_deck.from_troupe(self.player_troupe)
        self.action_deck: CardCollection = CardCollection(game)
        self.action_deck.generate_actions(20)

        # events
        self.event_deck: Dict[Dict] = {}
        events = self.game.data.events.values()
        # add events, broken down by tiers
        for event in events:
            self.event_deck[event["tier"]][event["type"]] = event

        # resources
        self.gold: int = 0
        self.rations: int = 0
        self.charisma: int = 0
        self.leadership: int = 0
        self.morale: int = 0

        # general
        self.level: int = 0

        # record duration
        end_time = time.time()
        logging.info(f"Memory: initialised in {format(end_time - start_time, '.2f')}s.")

    def amend_gold(self, amount: int):
        """
        Amend the current gold value by the given amount.
        """
        self.gold = max(0, self.gold + amount)

    def amend_rations(self, amount: int):
        """
        Amend the current rations value by the given amount.
        """
        self.rations = max(0, self.rations + amount)

    def amend_charisma(self, amount: int):
        """
        Amend the current charisma value by the given amount.
        """
        self.charisma = max(0, self.charisma + amount)

    def amend_leadership(self, amount: int):
        """
        Amend the current leadership value by the given amount.
        """
        self.leadership = max(0, self.leadership + amount)

    def amend_morale(self, amount: int):
        """
        Amend the current morale value by the given amount.
        """
        self.morale = max(0, self.morale + amount)

    def generate_id(self) -> int:
        """
        Create unique ID for an instance, such as a unit.
        """
        self._last_id += 1
        return self._last_id

    def get_random_event(self, tiers: List[int] = None) -> Dict:
        """
        Get a random event from the tiers specified. If no tiers specified then all are included. This event is then
        removed from the list of possible events.
        """
        events = self.event_deck

        # handle mutable default
        if tiers is None:
            tiers = [1, 2, 3, 4]  # all tiers

        possible_events = []
        possible_events_occur_rates = []
        for event in events:
            if event["level_available"] <= self.level and event["tier"] in tiers:
                possible_events.append(event)
                occur_rate = self.game.data.get_event_occur_rate(event["type"])
                possible_events_occur_rates.append(occur_rate)

        event_ = self.game.rng.choices(possible_events, possible_events_occur_rates)[0]

        events.pop(event_["type"])

        return event_


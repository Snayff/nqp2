from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import conditions as conditions

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
        self.event_deck: Dict = self._load_events([1])  # all available events
        self.priority_events: Dict = {}  # events to be prioritised

        # resources
        self.gold: int = 0
        self.rations: int = 0
        self.charisma: int = 0
        self.leadership: int = 0
        self.morale: int = 0

        # general
        self.level: int = 0
        self.flags: List[str] = []

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

    def get_random_event(self) -> Dict:
        """
        Get a random event from those available. This event is then removed from the list of possible events.
        """
        possible_events = []
        possible_events_occur_rates = []

        # priority or non-priority
        chance_of_priority = 33
        if self.game.rng.roll() < chance_of_priority:
            events = self.priority_events
        else:
            events = self.event_deck

        # grab events and occur rate
        for event in events.values():
            if event["level_available"] <= self.level and event["tier"] in tiers:
                possible_events.append(event)
                occur_rate = self.game.data.get_event_occur_rate(event["type"])
                possible_events_occur_rates.append(occur_rate)

        # choose an event
        event_ = self.game.rng.choices(possible_events, possible_events_occur_rates)[0]

        events.pop(event_["type"])

        return event_

    def _load_events(self, levels: Optional[List[int]] = None) -> Dict:
        # handle mutable default
        if levels is None:
            levels = [1, 2, 3, 4]  # all levels

        event_deck = {}
        events = self.game.data.events

        # add events
        for event in events.values():
            if event["level_available"] in levels:
                event_deck[event["type"]] = event

        return event_deck

    def _check_event_conditions(self, event: Dict) -> bool:
        """
        Return true if all an event's conditions are met.
        """
        conditions = event["conditions"]
        results = []

        for condition in conditions:
            key, condition_remainder = condition.split(":", 1)
            if "@" in condition_remainder:
                value, target = condition_remainder.split("@", 1)
            else:
                value = condition_remainder
                target = None
            results.append(self._check_event_condition(key, value, target))

        if all(results):
            outcome = True
        else:
            outcome = False
        return outcome


    def _check_event_condition(self, condition_key: str, condition_value: str, target: str) -> bool:
        """
        Check the condition given. Not all conditions use a target and in those cases the target is ignored.
        """
        outcome = False

        if condition_key == "flag":
            if condition_value in self.flags:
                outcome = True
            else:
                outcome = False

        else:
            logging.critical(f"Condition key specified ({condition_key}) is not known and was ignored.")

        return outcome

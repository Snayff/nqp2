from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.constants import DAYS_UNTIL_BOSS
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
        self.turns_since_priority_event: int = 0

        # resources
        self.gold: int = 0
        self.rations: int = 0
        self.charisma: int = 0
        self.leadership: int = 0
        self.morale: int = 0

        # general
        self.level: int = 0
        self.flags: List[str] = []
        self.days_until_boss: int = DAYS_UNTIL_BOSS

        # generated values for later user
        self.level_boss: str = ""

        # history
        self.seen_bosses: List[str] = []

        # record duration
        end_time = time.time()
        logging.info(f"Memory: initialised in {format(end_time - start_time, '.2f')}s.")

    def amend_gold(self, amount: int) -> int:
        """
        Amend the current gold value by the given amount. Return remaining amount.
        """
        self.gold = max(0, self.gold + amount)
        return self.gold

    def amend_rations(self, amount: int) -> int:
        """
        Amend the current rations value by the given amount. Return remaining amount.
        """
        self.rations = max(0, self.rations + amount)
        return self.rations

    def amend_charisma(self, amount: int) -> int:
        """
        Amend the current charisma value by the given amount. Return remaining amount.
        """
        self.charisma = max(0, self.charisma + amount)
        return self.charisma

    def amend_leadership(self, amount: int) -> int:
        """
        Amend the current leadership value by the given amount. Return remaining amount.
        """
        self.leadership = max(0, self.leadership + amount)
        return self.leadership

    def amend_morale(self, amount: int) -> int:
        """
        Amend the current morale value by the given amount. Return remaining amount.
        """
        self.morale = max(0, self.morale + amount)
        return self.morale

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
        if len(self.priority_events) >= 1:
            chance_of_priority = 33 * self.turns_since_priority_event
            if self.game.rng.roll() < chance_of_priority:
                events = self.priority_events
                self.turns_since_priority_event = 0  # reset count
            else:
                events = self.event_deck
                self.turns_since_priority_event += 1  # increment count
        else:
            events = self.event_deck

        # grab events and occur rate
        for event in events.values():
            if self._check_event_conditions(event):
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

    def prioritise_event(self, event_type: str):
        """
        Move an event from the event_deck to the priority events.
        """
        try:
            event = self.event_deck.pop(event_type)
            self.priority_events[event_type] = event

        except KeyError:
            logging.critical(f"Event ({event_type}) specified not found in Memory.event_deck and was ignored.")

    def generate_level_boss(self):
        """
        Generate the boss for the current level.
        """
        available_bosses = []

        for boss in self.game.data.bosses.values():
            if boss["level_available"] <= self.level and boss["type"] not in self.seen_bosses:
                available_bosses.append(boss["type"])

        chosen_boss = self.game.rng.choice(available_bosses)
        self.level_boss = chosen_boss

        self.seen_bosses.append(chosen_boss)

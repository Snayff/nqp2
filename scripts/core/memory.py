from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.card_collection import CardCollection
from scripts.scenes.combat.elements.commander import Commander
from scripts.scenes.combat.elements.entity import Entity
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

        self._game: Game = game

        # units
        self._last_id = 0

        # empty values will be overwritten in run_start
        self.player_troupe: Troupe = Troupe(self._game, "player", [])
        self.commander: Optional[Commander] = None

        #############################
        # TODO  i dont like any of this. rewrite it
        # self.player_actions = ["fireball"]
        # self.unit_deck: CardCollection = CardCollection(game)
        # self.unit_deck.from_troupe(self.player_troupe)
        # self.action_deck: CardCollection = CardCollection(game)
        # self.action_deck.generate_actions(20)
        ################################

        # events
        self._event_deck: Dict = self._load_events([1])  # all available events
        self._priority_events: Dict = {}  # events to be prioritised
        self._turns_since_priority_event: int = 0

        # resources
        self.gold: int = 0
        self.rations: int = 0
        self.charisma: int = 0
        self.leadership: int = 0
        self.morale: int = 0

        # progress
        self.level: int = 0
        self.flags: List[str] = []

        # generated values for later user
        self.level_boss: str = ""

        # history
        self._seen_bosses: List[str] = []

        # record duration
        end_time = time.time()
        logging.debug(f"Memory: initialised in {format(end_time - start_time, '.2f')}s.")

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
        if len(self._priority_events) >= 1:
            chance_of_priority = 33 * self._turns_since_priority_event
            if self._game.rng.roll() < chance_of_priority:
                events = self._priority_events
                self._turns_since_priority_event = 0  # reset count
            else:
                events = self._event_deck
                self._turns_since_priority_event += 1  # increment count
        else:
            events = self._event_deck

        # grab events and occur rate
        for event in events.values():
            if self._check_event_conditions(event):
                possible_events.append(event)
                occur_rate = self._game.data.get_event_occur_rate(event["type"])
                possible_events_occur_rates.append(occur_rate)

        # choose an event
        event_ = self._game.rng.choices(possible_events, possible_events_occur_rates)[0]

        events.pop(event_["type"])

        return event_

    def get_event(self, event_id: str, remove_from_pool: bool):
        """
        Get a specific event. remove_from_pool determines whether the event is removed from the list of possible
        events.
        """
        try:
            if remove_from_pool:
                event = self._event_deck.pop(event_id)
            else:
                event = self._event_deck[event_id]

            return event
        except KeyError:
            logging.error(f"Event ID ({event_id}) not found.")
            raise Exception

    def _load_events(self, levels: Optional[List[int]] = None) -> Dict:
        # handle mutable default
        if levels is None:
            levels = [1, 2, 3, 4]  # all levels

        event_deck = {}
        events = self._game.data.events

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
            event = self._event_deck.pop(event_type)
            self._priority_events[event_type] = event

        except KeyError:
            logging.critical(f"Event ({event_type}) specified not found in Memory.event_deck and was ignored.")

    def generate_level_boss(self):
        """
        Generate the boss for the current level.
        """
        available_bosses = []

        for boss in self._game.data.bosses.values():
            if boss["level_available"] <= self.level and boss["type"] not in self._seen_bosses:
                available_bosses.append(boss["type"])

        chosen_boss = self._game.rng.choice(available_bosses)
        self.level_boss = chosen_boss

        self._seen_bosses.append(chosen_boss)

    def get_all_entities(self) -> List[Entity]:
        """
        Get a list of all entities
        """
        entities = []
        entities += self.player_troupe.entities

        return entities

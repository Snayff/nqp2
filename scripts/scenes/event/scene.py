from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import EventState, SceneType
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.combat.elements.unit import Unit
from scripts.scenes.event.ui import EventUI

if TYPE_CHECKING:
    from typing import Any, Dict, List, Tuple

    from scripts.core.game import Game

__all__ = ["EventScene"]


class EventScene(Scene):
    """
    Handles EventScene interactions and consolidates the rendering. EventScene is used to give players a text choice.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.EVENT)

        self.ui: EventUI = EventUI(game, self)

        self.state: EventState = EventState.MAKE_DECISION

        self.active_event: Dict = {}
        self.event_resources = {}  # resources needed for the event
        self.triggered_results: List[str] = []  # the list of result strings from the selected option
        self.events_triggered: int = 0  # num events triggered this level

        # record duration
        end_time = time.time()
        logging.debug(f"EventScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = EventUI(self._game, self)

        self.active_event = {}

    def load_random_event(self):
        self.active_event = self._game.memory.get_random_event()

        logging.info(f"Event {self.active_event['type']} loaded.")

        self._load_event_resources()

    def load_event(self, event_id: str, remove_from_pool: bool = False):
        """
        Load a specific event.
        """
        event = self._game.memory.get_event(event_id, remove_from_pool)

        self.active_event = event
        logging.info(f"Event {self.active_event['type']} loaded.")
        self._load_event_resources()

    def _load_event_resources(self):
        self.event_resources = {}

        for resource_str in self.active_event["resources"]:
            key, value, target = self.parse_event_string(resource_str)
            resource = self._generate_event_resource(key, target)
            if resource is not None:
                self.event_resources[value] = resource
            else:
                event_type = self.active_event["type"]
                logging.critical(f"Event resources ({event_type}:{key}) returned none and was ignored.")

    def _generate_event_resource(self, resource_key: str, resource_target: str) -> Any:
        """
        Create a resource based on the given key.
        """
        resource = None

        if resource_key == "existing_unit":
            unit = None
            units = list(self._game.memory.player_troupe.units.values())

            # shuffle list
            self._game.rng.shuffle(units)

            # ensure a unique resource
            for unit in units:
                if unit not in self.event_resources:
                    break

            resource = unit

        elif resource_key == "new_specific_unit":
            if resource_target in self._game.data.units:
                troupe = Troupe(self._game, "player", self._game.memory.player_troupe.allies)
                unit_id = troupe.generate_specific_units([resource_target])[0]
                resource = troupe.units[unit_id]

            else:
                logging.warning(
                    f"Unit type ({resource_target}) specified does not exist. No resource was  " f"created."
                )

        elif resource_key == "new_random_unit":
            if resource_target is None:
                tiers = None
            else:
                tiers = [int(resource_target)]

            troupe = Troupe(self._game, "player", self._game.memory.player_troupe.allies)
            unit_id = troupe.generate_units(1, tiers)[0]
            resource = troupe.units[unit_id]

        return resource

    def _trigger_result(self):
        """
        Trigger the result for the previously selected option.

        Results are a list of key value target strings. "result_action : result_value @ target"

        Example:
            ["Gold:10","Gold:10"] - would add 10 gold twice.
        """
        for result in self.triggered_results:
            key, value, target = self.parse_event_string(result)
            self._action_result(key, value, target)

    @staticmethod
    def parse_event_string(result: str) -> Tuple[str, str, str]:
        """
        Break event string into component parts. Applicable for Conditions, Resources and Results. (or anything that
        has a syntax of key:value@target.

        Returns a tuple of key, value, target.
        """
        key, result_remainder = result.split(":", 1)
        if "@" in result_remainder:
            value, target = result_remainder.split("@", 1)
        else:
            value = result_remainder
            target = None

        return key, value, target

    def _action_result(self, result_key: str, result_value: str, target: str):
        """
        Resolve the action from the result. Not all actions need a target and in those cases the target is ignored.
        """
        if result_key == "gold":
            original_value = self._game.memory.gold
            self._game.memory.amend_gold(int(result_value))
            logging.info(f"Gold changed by {result_value};  {original_value} -> {self._game.memory.gold}.")

        elif result_key == "rations":
            original_value = self._game.memory.rations
            self._game.memory.amend_rations(int(result_value))
            logging.info(f"Rations changed by {result_value};  {original_value} -> {self._game.memory.rations}.")

        elif result_key == "morale":
            original_value = self._game.memory.morale
            self._game.memory.amend_morale(int(result_value))
            logging.info(f"Morale changed by {result_value};  {original_value} -> {self._game.memory.morale}.")

        elif result_key == "charisma":
            original_value = self._game.memory.charisma
            self._game.memory.amend_charisma(int(result_value))
            logging.info(f"Charisma changed by {result_value};  {original_value} -> {self._game.memory.charisma}.")

        elif result_key == "leadership":
            original_value = self._game.memory.leadership
            self._game.memory.amend_leadership(int(result_value))
            logging.info(f"Leadership changed by {result_value};  {original_value} -> {self._game.memory.leadership}.")

        elif result_key == "injury":
            try:
                resource = self.event_resources[target]
                assert isinstance(resource, Unit)
                for count in range(0, int(result_value)):
                    # TODO - add injury allocation
                    pass

                logging.warning(
                    f"Injuries don't yet exist, but {resource.type}:{resource.id} should have been "
                    f"given {result_value} of them just now."
                )

            except KeyError:
                logging.warning(
                    f"Target specified ({target}) is not found in resources ({self.event_resources})"
                    f" and was ignored."
                )

        elif result_key == "unlock_event":
            # add flag to show unlocked
            self._game.memory.flags.append(result_value + "_unlocked")

            self._game.memory.prioritise_event(result_value)

        elif result_key == "add_unit_resource":
            try:
                unit = self.event_resources[result_value]

                # check doesnt already exist
                if unit not in self._game.memory.player_troupe.units:
                    self._game.memory.player_troupe.add_unit(unit)
                else:
                    logging.warning(f"Target specified ({target}) is an existing unit and was therefore ignored.")

            except KeyError:
                logging.warning(
                    f"Target specified ({target}) is not found in resources ({self.event_resources})"
                    f" and was ignored."
                )

        elif result_key == "add_specific_unit":
            if result_value in self._game.data.units:
                self._game.memory.player_troupe.generate_specific_units([result_value])

            else:
                logging.warning(f"Unit type ({result_value}) specified does not exist. No unit was added.")

        else:
            logging.warning(f"Result key specified ({result_key}) is not known and was ignored.")

    def roll_for_event(self) -> bool:
        """
        Roll to see if an event will be triggered when transitioning between nodes. True for event due.
        """
        # check if we have hit the limit of events
        if self.events_triggered >= self._game.data.config["overworld"]["max_events_per_level"]:
            return False

        if self._game.rng.roll() < self._game.data.config["overworld"]["chance_of_event"]:
            return True

        # safety catch
        return False

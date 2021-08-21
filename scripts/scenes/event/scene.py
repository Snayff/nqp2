from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import EventState
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.combat.elements.unit import Unit
from scripts.scenes.event.ui import EventUI

if TYPE_CHECKING:
    from typing import Any, Dict

    from scripts.core.game import Game

__all__ = ["EventScene"]


class EventScene(Scene):
    """
    Handles EventScene interactions and consolidates the rendering. EventScene is used to give players a text choice.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: EventUI = EventUI(game)

        self.state: EventState = EventState.MAKE_DECISION

        self.active_event: Dict = {}
        self.event_resources = {}  # resources needed for the event

        # record duration
        end_time = time.time()
        logging.info(f"EventScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def reset(self):
        self.ui = EventUI(self.game)

        self.active_event = {}

    def load_random_event(self):
        self.active_event = self.game.memory.get_random_event()
        self._load_event_resources()

    def load_event(self, event_id: str, remove_from_pool: bool = False):
        """
        Load a specific event.
        """
        if remove_from_pool:
            event = self.game.memory.event_deck.pop(event_id)
        else:
            event = self.game.memory.event_deck[event_id]

        self.active_event = event
        self._load_event_resources()

    def _load_event_resources(self):
        self.event_resources = {}

        for resource in self.active_event["resources"]:
            key, identifier = resource.split(":", 1)
            resource_ = self._generate_event_resource(key)
            if resource_ is not None:
                self.event_resources[identifier] = resource_
            else:
                event_type = self.active_event["type"]
                logging.critical(f"Event resources ({event_type}:{key}) returned none and was ignored.")

    def _generate_event_resource(self, resource_key: str) -> Any:
        if resource_key == "existing_unit":
            unit = None
            units = list(self.game.memory.player_troupe.units.values())

            # shuffle list
            self.game.rng.shuffle(units)

            # ensure a unique resource
            for unit in units:
                if unit not in self.event_resources:
                    break

            return unit

    def trigger_result(self, option_index: int):
        """
        Trigger the result for the indicated option.

        Results are a list of key value target strings. "result_action : result_value @ target"

        Example:
            ["Gold:10","Gold:10"] - would add 10 gold twice.
        """
        results = self.active_event["options"][option_index]["result"]

        for result in results:
            key, result_remainder = result.split(":", 1)
            if "@" in result_remainder:
                value, target = result_remainder.split("@", 1)
            else:
                value = result_remainder
                target = None
            self._action_result(key, value, target)

    def _action_result(self, result_key: str, result_value: str, target: str):
        """
        Resolve the action from the result. Not all actions need a target and in those cases the target is ignored.
        """
        if result_key == "gold":
            original_value = self.game.memory.gold
            self.game.memory.amend_gold(int(result_value))
            logging.info(f"Gold changed by {result_value};  {original_value} -> {self.game.memory.gold}.")

        elif result_key == "rations":
            original_value = self.game.memory.rations
            self.game.memory.amend_rations(int(result_value))
            logging.info(f"Rations changed by {result_value};  {original_value} -> {self.game.memory.rations}.")

        elif result_key == "morale":
            original_value = self.game.memory.morale
            self.game.memory.amend_morale(int(result_value))
            logging.info(f"Morale changed by {result_value};  {original_value} -> {self.game.memory.morale}.")

        elif result_key == "charisma":
            original_value = self.game.memory.charisma
            self.game.memory.amend_charisma(int(result_value))
            logging.info(f"Charisma changed by {result_value};  {original_value} -> {self.game.memory.charisma}.")

        elif result_key == "leadership":
            original_value = self.game.memory.leadership
            self.game.memory.amend_leadership(int(result_value))
            logging.info(f"Leadership changed by {result_value};  {original_value} -> {self.game.memory.leadership}.")

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
                logging.critical(
                    f"Target specified ({target}) is not found in resources ({self.event_resources})"
                    f" and was ignored."
                )

        elif result_key == "unlock_event":
            # add flag to show unlocked
            self.game.memory.flags.append(result_value + "_unlocked")

            self.game.memory.prioritise_event(result_value)

        else:
            logging.critical(f"Result key specified ({result_key}) is not known and was ignored.")

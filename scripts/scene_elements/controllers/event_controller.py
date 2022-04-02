from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.animation import Animation
from scripts.core.base_classes.controller import Controller
from scripts.core.base_classes.image import Image
from scripts.core.constants import DEFAULT_IMAGE_SIZE, EventState
from scripts.core.debug import Timer
from scripts.scene_elements.troupe import Troupe
from scripts.scene_elements.unit import Unit

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["EventController"]


class EventController(Controller):
    """
    Event game functionality and event-only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("EventController initialised"):
            super().__init__(game, parent_scene)

            self.state: EventState = EventState.IDLE
            self.active_event: Dict = {}
            self.event_resources: Dict = {}  # resources needed for the event
            self.current_index: int = 0  # the event option chosen

    def update(self, delta_time: float):
        pass

    def reset(self):
        self.state = EventState.IDLE
        self.active_event = {}
        self.event_resources = {}
        self.current_index = 0

        self.load_random_event()

    def load_random_event(self):
        self.active_event = self.get_random_event()

        logging.info(f"Event {self.active_event['type']} loaded.")

        self._load_event_resources()

    def load_event(self, event_id: str, remove_from_pool: bool = False):
        """
        Load a specific event.
        """
        event = self.get_event(event_id, remove_from_pool)

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
            units = list(self._parent_scene.model.player_troupe.units.values())

            # shuffle list
            self._game.rng.shuffle(units)

            # ensure a unique resource
            for unit in units:
                if unit not in self.event_resources:
                    break

            resource = unit

        elif resource_key == "new_specific_unit":
            if resource_target in self._game.data.units:
                troupe = Troupe(self._game, "player", self._parent_scene.model.player_troupe.allies)
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

            troupe = Troupe(self._game, "player", self._parent_scene.model.player_troupe.allies)
            unit_id = troupe.generate_units(1, tiers)[0]
            resource = troupe.units[unit_id]

        return resource

    def trigger_result(self):
        """
        Trigger the result for the option at the select current_index.

        Results are a list of key value target strings. "result_action : result_value @ target"

        Example:
            ["Gold:10","Gold:10"] - would add 10 gold twice.
        """
        logging.info(
            f"Choose option {self.current_index}, " f"{self.active_event['options'][self.current_index]['text']}."
        )
        for result in self.active_event["options"][self.current_index]["result"]:
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
            original_value = self._parent_scene.model.gold
            self._parent_scene.model.amend_gold(int(result_value))
            logging.info(f"Gold changed by {result_value};  {original_value} -> {self._parent_scene.model.gold}.")

        elif result_key == "rations":
            original_value = self._parent_scene.model.rations
            self._parent_scene.model.amend_rations(int(result_value))
            logging.info(f"Rations changed by {result_value};  {original_value} -> {self._parent_scene.model.rations}.")

        elif result_key == "morale":
            original_value = self._parent_scene.model.morale
            self._parent_scene.model.amend_morale(int(result_value))
            logging.info(f"Morale changed by {result_value};  {original_value} -> {self._parent_scene.model.morale}.")

        elif result_key == "charisma":
            original_value = self._parent_scene.model.charisma
            self._parent_scene.model.amend_charisma(int(result_value))
            logging.info(
                f"Charisma changed by {result_value};  {original_value} -> " f"{self._parent_scene.model.charisma}. "
            )

        elif result_key == "leadership":
            original_value = self._parent_scene.model.leadership
            self._parent_scene.model.amend_leadership(int(result_value))
            logging.info(
                f"Leadership changed by {result_value};  {original_value} -> "
                f"{self._parent_scene.model.leadership}. "
            )

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

            self.prioritise_event(result_value)

        elif result_key == "add_unit_resource":
            try:
                unit = self.event_resources[result_value]

                # check doesnt already exist
                if unit not in self._parent_scene.model.player_troupe.units:
                    self._parent_scene.model.player_troupe.add_unit(unit)
                else:
                    logging.warning(f"Target specified ({target}) is an existing unit and was therefore ignored.")

            except KeyError:
                logging.warning(
                    f"Target specified ({target}) is not found in resources ({self.event_resources})"
                    f" and was ignored."
                )

        elif result_key == "add_specific_unit":
            if result_value in self._game.data.units:
                self._parent_scene.model.player_troupe.generate_specific_units([result_value])

            else:
                logging.warning(f"Unit type ({result_value}) specified does not exist. No unit was added.")

        else:
            logging.warning(f"Result key specified ({result_key}) is not known and was ignored.")

    def get_result_image(self, result_key: str, result_value: str, result_target: str) -> Union[Image, Animation]:
        """
        Get an image for the result key given.
        """
        icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        if result_key == "gold":
            image = self._game.visual.get_image("gold", icon_size)

        elif result_key == "rations":
            image = self._game.visual.get_image("rations", icon_size)

        elif result_key == "morale":
            image = self._game.visual.get_image("morale", icon_size)

        elif result_key == "charisma":
            image = self._game.visual.get_image("charisma", icon_size)

        elif result_key == "leadership":
            image = self._game.visual.get_image("leadership", icon_size)

        elif result_key == "injury":
            image = self._game.visual.get_image("injury", icon_size)

        elif result_key == "add_unit_resource":
            unit = self.event_resources[result_value]
            image = self._game.visual.create_animation(unit.type, "icon")

        elif result_key == "add_specific_unit":
            image = self._game.visual.create_animation(result_value, "icon")

        else:
            logging.warning(f"Result key not recognised. Image not found used.")
            image = self._game.visual.get_image("not_found", icon_size)

        return image

    def get_random_event(self) -> Dict:
        """
        Get a random event from those available. This event is then removed from the list of possible events.
        """
        possible_events = []
        possible_events_occur_rates = []

        # priority or non-priority
        if len(self._parent_scene.model.priority_events) >= 1:
            chance_of_priority = 33 * self._parent_scene.model.turns_since_priority_event
            if self._game.rng.roll() < chance_of_priority:
                events = self._parent_scene.model.priority_events
                self._parent_scene.model.turns_since_priority_event = 0  # reset count
            else:
                events = self._parent_scene.model.event_deck
                self._parent_scene.model.turns_since_priority_event += 1  # increment count
        else:
            events = self._parent_scene.model.event_deck

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
                event = self._parent_scene.model.event_deck.pop(event_id)
            else:
                event = self._parent_scene.model.event_deck[event_id]

            return event
        except KeyError:
            logging.error(f"Event ID ({event_id}) not found.")
            raise Exception

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
            if condition_value in self._game.memory.flags:
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
            event = self._parent_scene.model.event_deck.pop(event_type)
            self._parent_scene.model.priority_events[event_type] = event

        except KeyError:
            logging.critical(f"Event ({event_type}) specified not found in event_deck and was ignored.")

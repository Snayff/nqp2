from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from snecs.typedefs import EntityID

from nqp.command.unit import Unit

if TYPE_CHECKING:
    from typing import Dict, List

    from nqp.core.game import Game

__all__ = ["Troupe"]


class Troupe:
    """
    Management of a group of units
    """

    def __init__(self, game: Game, team: str, allies: List[str]):
        self._game: Game = game

        self._unit_ids: List[int] = []  # used to manage order
        self._units: Dict[int, Unit] = {}
        self.team: str = team
        self.allies: List[str] = allies
        self._position: pygame.Vector2 = self._get_reference_position()

    def update(self, delta_time: float):
        for unit in self.units.values():
            unit.update(delta_time)

        self._position = self._get_reference_position()

    @property
    def units(self) -> Dict[int, Unit]:
        units_ = {}

        # build new dict respecting order
        for id_ in self._unit_ids:
            units_[id_] = self._units[id_]

        return units_

    @property
    def entities(self) -> List[EntityID]:
        entities = []
        for unit in self.units.values():
            entities += unit.entities
        return entities

    def debug_init_units(self) -> List[int]:
        """
        Initialise all units for Troupe faction. Returns list of created ids.
        """
        ids = []

        unit_types = self._game.data.get_units_by_category(self.allies)
        for unit_type in unit_types:
            id_ = self._add_unit_from_type(unit_type)
            ids.append(id_)

        return ids

    def add_unit(self, unit: Unit):
        """
        Add a unit instance to the troupe. Used when buying an existing unit, e.g. from Inn.
        """
        self._units[unit.id] = unit
        self._unit_ids.append(unit.id)

        self._game.world.ui.grid.move_to_empty_cell(unit)  # Assigns the new unit to an empty cell

        logging.debug(f"Unit {unit.type}({unit.id}) added to {self.team}'s troupe.")

    def _add_unit_from_type(self, unit_type: str) -> int:
        """
        Create a unit based on the unit type and add the unit to the troupe. Return id.
        """

        id_ = self._game.memory.generate_id()
        unit = Unit(self._game, id_, unit_type, self.team, pygame.Vector2(0, 0))
        unit.spawn_entities()
        self._units[id_] = unit
        self._unit_ids.append(id_)

        logging.debug(f"Unit {unit.type}({unit.id}) created and added to {self.team}'s troupe.")

        return id_

    def remove_unit(self, id_: int):
        try:
            unit = self._units.pop(id_)
            self._unit_ids.remove(id_)

            logging.debug(f"Unit {unit.type}({unit.id}) removed from {unit.team}'s troupe.")

        except KeyError:
            logging.warning(f"remove_unit: {id_} not found in {self.units}. No unit removed.")

    def remove_all_units(self):
        """
        Remove all units from the Troupe
        """
        self._units = {}
        self._unit_ids = []

        logging.debug(f"All units removed from {self.team}'s troupe.")

    def generate_units(
        self,
        number_of_units: int,
        tiers_allowed: List[int] = None,
        duplicates: bool = False,
    ) -> List[int]:
        """
        Generate units for the Troupe, based on parameters given.

        Returns:
             list of created ids.

        """

        unit_types = []

        # get unit info
        unit_types_ = []
        unit_occur_rate = []
        for unit_type in self._game.data.get_units_by_category(self.allies, tiers_allowed):
            unit_types_.append(unit_type)
            occur_rate = self._game.data.get_unit_occur_rate(unit_type)
            unit_occur_rate.append(occur_rate)

        # choose units
        if duplicates:
            chosen_types = self._game.rng.choices(unit_types_, unit_occur_rate, k=number_of_units)

        else:
            chosen_types = []

            for i in range(number_of_units):
                # choose unit
                unit = self._game.rng.choices(unit_types_, unit_occur_rate)[0]
                chosen_types.append(unit)

                # remove unit and occur rate from option pool
                unit_index = unit_types_.index(unit)
                unit_types_.remove(unit)
                del unit_occur_rate[unit_index]

        # add to list
        for chosen_type in chosen_types:
            unit_types.append(chosen_type)

        # create units
        ids = []
        for unit_type in unit_types:
            id_ = self._add_unit_from_type(unit_type)
            ids.append(id_)

        return ids

    def generate_specific_units(self, unit_types: List[str]) -> List[int]:
        """
        Generate units for the Troupe, based on parameters given. Returns list of created ids.

        unit_types is expressed as [unit.type, ...]
        """
        # create units
        ids = []
        for unit_type in unit_types:
            id_ = self._add_unit_from_type(unit_type)
            ids.append(id_)

        return ids

    def upgrade_unit(self, id_: int, upgrade_type: str):
        """
        Upgrade a unit with a given upgrade.
        """
        # get unit
        unit = self.units[id_]

        try:
            data = self._game.data.upgrades[upgrade_type]
            unit.add_modifier(data["stat"], data["mod_amount"])

        except KeyError:
            logging.warning(f"Tried to upgrade {unit.id} with {upgrade_type} but upgrade not found. No action taken.")

    def get_random_unit(self) -> Unit:
        """
        Return a random unit from the Troupe.
        """
        id_ = self._game.rng.choice(self.units)
        return self.units[id_]

    def set_force_idle(self, active: bool):
        """
        Set the forced_idle attr for all units in the Troupe
        """
        for unit in self.units.values():
            unit.forced_behaviour = False
            unit.forced_idle = active

    def _get_reference_position(self) -> pygame.Vector2:
        """
        Get the Troupe's reference position, using the position of the first Entity in the dict.
        """
        if len(self.units) > 0:
            unit = list(self.units.values())[0]
            return unit.pos
        else:
            return pygame.Vector2(0, 0)

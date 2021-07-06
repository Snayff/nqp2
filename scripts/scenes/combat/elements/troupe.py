from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.commander import Commander
from scripts.scenes.combat.elements.unit import Unit

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Optional

    from scripts.core.game import Game

__all__ = ["Troupe"]


class Troupe:
    """
    Management of a group of units
    """

    def __init__(self, game: Game, team: str, allies: List[str]):
        self.game: Game = game

        self._unit_ids: List[int] = []  # used to manage order
        self._units: Dict[int, Unit] = {}
        self.team: str = team
        self.allies: List[str] = allies


    @property
    def units(self) -> Dict[int, Unit]:
        units_ = {}

        # build new dict respecting order
        for id_ in self._unit_ids:
            units_[id_] = self._units[id_]

        return units_

    def debug_init_units(self) -> List[int]:
        """
        Initialise all units for Troupe home. Returns list of created ids.
        """
        ids = []

        unit_types = self.game.data.get_units_by_category(self.allies)
        for unit_type in unit_types:
            id_ = self.add_unit_from_type(unit_type)
            ids.append(id_)

        return ids

    def add_unit(self, unit: Unit):
        """
        Add a unit instance to the troupe. Used when buying an existing unit, e.g. from Inn.
        """
        self._units[unit.id] = unit
        self._unit_ids.append(unit.id)

        logging.info(f"Unit {unit.type}({unit.id}) added to {self.team}'s troupe.")

    def add_unit_from_type(self, unit_type: str) -> int:
        """
        Create a unit based on the unit type and add the unit to the troupe. Return id.
        """
        id_ = self.game.memory.generate_id()
        unit = Unit(self.game, id_, unit_type, self.team)
        self._units[id_] = unit
        self._unit_ids.append(id_)

        logging.info(f"Unit {unit.type}({unit.id}) created and added to {self.team}'s troupe.")

        return id_

    def remove_unit(self, id_: int):
        try:
            print(f"_units (pre-pop): {self._units}")
            unit = self._units.pop(id_)
            print(f"_units (post-pop): {self._units}")

            print(f"_unit_ids (pre-pop): {self._unit_ids}")
            self._unit_ids.remove(id_)
            print(f"_unit_ids (post-pop): {self._unit_ids}")

            logging.info(f"Unit {unit.type}({unit.id}) removed from {unit.team}'s troupe.")
        except KeyError:
            logging.warning(f"remove_unit: {id_} not found in {self.units}. No unit removed.")

    def remove_all_units(self):
        """
        Remove all units from the Troupe
        """
        self._units = {}
        self._unit_ids = []

        logging.info(f"All units removed from {self.team}'s troupe.")

    def generate_units(
        self, number_of_units: int, tiers_allowed: List[int] = None, unit_types: List[str] = None
    ) -> List[int]:
        """
        Generate units for the Troupe, based on parameters given. If no unit types are given then any unit type can
        be chosen from home and ally. Returns list of created ids.

        unit_types is expressed as [unit.type, ...]
        """
        # handle default mutable
        if unit_types is None:
            unit_types = []

            # get unit info
            unit_types_ = []
            unit_occur_rate = []
            for unit_type in self.game.data.get_units_by_category(self.allies, tiers_allowed):
                unit_types_.append(unit_type)
                occur_rate = self.game.data.get_unit_occur_rate(unit_type)
                unit_occur_rate.append(occur_rate)

            # choose units
            chosen_types = self.game.rng.choices(unit_types_, unit_occur_rate, k=number_of_units)

            # identify which are upgrades
            for chosen_type in chosen_types:
                unit_types.append(chosen_type)

        # create units
        ids = []
        for unit_type in unit_types:
            id_ = self.add_unit_from_type(unit_type)
            ids.append(id_)

        return ids

    def upgrade_unit(self, id_: int):
        """
        Upgrade a unit, if it has an upgrade.
        """
        # get unit
        unit = self.units[id_]

        # confirm there is an upgrade
        if not unit.upgrades_to:
            logging.warning(f"Tried to upgrade {unit.type} but it cannot be upgraded further.")
            return

        # create upgraded unit. Not using add methods so that we can set position
        new_id = self.game.memory.generate_id()
        upgraded_unit = Unit(self.game, new_id, unit.upgrades_to, self.team)
        self._units[new_id] = upgraded_unit

        # insert after the existing unit
        self._unit_ids.insert(self._unit_ids.index(id_) + 1, new_id)

        # remove non upgraded unit
        self.remove_unit(id_)

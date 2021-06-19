from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.unit import Unit

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from scripts.core.game import Game

__all__ = ["Troupe"]


class Troupe:
    """
    Management of a group of units
    """

    def __init__(self, game, team: str):
        self.game: Game = game

        self.units: Dict[int, Unit] = {}
        self.team: str = team

        self._last_id = 0

    def debug_init_units(self):
        """
        Initialise some units. For testing.
        """
        for i in range(4):
            if i % 2 == 1:
                self.add_unit_from_type("spearman")
            else:
                self.add_unit_from_type("spearman", True)

    def add_unit(self, unit: Unit):
        """
        Add a unit instance to the troupe. Used when buying an existing unit, e.g. from Inn.
        """
        self.units[unit.id] = unit
        logging.info(f"Unit {unit.type}({unit.id}) added to {self.team}'s troupe.")

    def add_unit_from_type(self, unit_type: str, is_upgraded: bool = False) -> int:
        """
        Create a unit based on the unit type and add the unit to the troupe. Return id.
        """
        id_ = self.game.memory.generate_id()
        unit = Unit(self.game, id_, unit_type, self.team, is_upgraded)
        self.units[id_] = unit

        logging.info(f"Unit {unit.type}({unit.id}) created and added to {self.team}'s troupe.")

        return id_

    def remove_unit(self, id_: int):
        try:
            unit = self.units.pop(id_)
            logging.info(f"Unit {unit.type}({unit.id}) removed from {unit.team}'s troupe.")
        except KeyError:
            logging.warning(f"remove_unit: {id_} not found in {self.units}. No unit removed.")

    def remove_all_units(self):
        """
        Remove all units from the Troupe
        """
        self.units = {}

    def generate_units(self, number_of_units: int, unit_types: List[Tuple[str, bool]] = None):
        """
        Generate units for the Troupe, based on parameters given. If no unit types are given then any unit type can
        be chosen.

        unit_types is expressed as [(unit.name, unit.is_upgraded), ...]
        """
        # handle default mutable
        if unit_types is None:
            unit_types = []

            # get unit info
            unit_types_ = []
            unit_rarity = []
            for unit_details in self.game.data.units.values():

                # get upgrades and non upgrades
                for is_upgraded_ in range(1):
                    if is_upgraded_:
                        unit_type_ = unit_details["type"] + "_upgraded"
                    else:
                        unit_type_ = unit_details["type"]

                    unit_types_.append(unit_type_)
                    unit_rarity.append(unit_details["rarity"][is_upgraded_])

            # choose units
            chosen_types = random.choices(unit_types_, unit_rarity, k=number_of_units)

            # identify which are upgrades
            for chosen_type in chosen_types:
                if "_upgraded" in chosen_type:
                    unit_types.append((chosen_type.replace("_upgraded", ""), True))
                else:
                    unit_types.append((chosen_type, False))

        # create units
        for unit_type, is_upgraded in unit_types:
            self.add_unit_from_type(unit_type, is_upgraded)

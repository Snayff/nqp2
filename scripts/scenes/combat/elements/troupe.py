from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.scenes.combat.elements.unit import Unit

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["Troupe"]


class Troupe:
    def __init__(self, game):
        self.game: Game = game

        self.units: Dict[int, Unit] = {}

        self._last_id = 0

    def debug_init_units(self):
        """
        Initialise some units. For testing.
        """
        for i in range(4):
            self.add_unit("spearman", "player")

    def add_unit(self, unit_type: str, team: str) -> int:
        """
        Add a unit to the troupe. Return id.
        """
        id_ = self._generate_id()
        unit = Unit(self.game, id_, unit_type, team)
        self.units[id_] = unit

        logging.info(f"Unit {unit.type}({unit.id}) added to {team}'s troupe.")

        return id_

    def remove_unit(self, id_: int):
        try:
            unit = self.units.pop(id_)
            logging.info(f"Unit {unit.type}({unit.id}) removed from {unit.team}'s troupe.")
        except KeyError:
            logging.warning(f"remove_unit: {id_} not found in {self.units}. No unit removed.")

    def _generate_id(self) -> int:
        """
        Create unique ID for a unit
        """
        self._last_id += 1
        return self._last_id
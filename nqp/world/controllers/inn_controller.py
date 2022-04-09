from __future__ import annotations

from typing import TYPE_CHECKING

from nqp.base_classes.controller import Controller
from nqp.core.constants import InnState
from nqp.core.debug import Timer
from nqp.command.troupe import Troupe

if TYPE_CHECKING:
    from typing import List, Optional

    from nqp.core.game import Game
    from nqp.scenes.world.scene import WorldScene
    from nqp.command.unit import Unit

__all__ = ["InnController"]


class InnController(Controller):
    """
    Inn game functionality and inn-only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("InnController: initialised"):
            super().__init__(game, parent_scene)

            self.state: InnState = InnState.IDLE
            self.units_available: List[Optional[Unit]] = []
            self.selected_unit: Optional[Unit] = None
            self.num_units: int = 3
            self.troupe_id: Optional[int] = None  # inn troupe id

            self.generate_units()

    def update(self, delta_time: float):
        pass

    def reset(self):
        if self.troupe_id:
            self.delete_troupe()
            self.troupe_id = None

        self.selected_unit = None
        self.units_available = []

        self.generate_units()

    def generate_units(self):
        """
        Generate units to sell. NOTE: currently hard coded.
        """
        # reset existing upgrades
        self.troupe_id = None
        self.units_available = []

        allies = self._parent_scene.model.player_troupe.allies

        # check allies have been initialised
        if len(allies) == 0:
            return

        inn_troupe = Troupe(self._game, "inn", allies)
        inn_troupe.generate_units(self.num_units)  # TODO - add tier
        self.troupe_id = self._parent_scene.model.add_troupe(inn_troupe)

        for unit in inn_troupe.units.values():
            self.units_available.append(unit)

    def recruit_unit(self, unit: Unit):
        """
        Add the unit to the player's Troupe and remove from the inn's.
        """
        self._parent_scene.model.amend_gold(unit.gold_cost)

        self._parent_scene.model.player_troupe.add_unit(unit)

        inn_troupe = self._parent_scene.model.troupes[self.troupe_id]
        inn_troupe.remove_unit(unit.id)

        # clear option from list
        index = self.units_available.index(self.selected_unit)
        self.units_available[index] = None

    def delete_troupe(self):
        """
        Delete the inn troupe.
        """
        self._parent_scene.model.remove_troupe(self.troupe_id)

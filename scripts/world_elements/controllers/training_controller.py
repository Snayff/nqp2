from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import TrainingState
from scripts.core.debug import Timer

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game
    from scripts.world_elements.unit import Unit
    from scripts.scenes.world.scene import WorldScene

__all__ = ["TrainingController"]


class TrainingController(Controller):
    """
    Training game functionality and training-only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("TrainingController initialised"):
            super().__init__(game, parent_scene)

            self.state: TrainingState = TrainingState.IDLE
            self.upgrades_available: List[Optional[Dict]] = []  # None/upgrade dict
            self.selected_upgrade: Optional[Dict] = None  # None/upgrade dict
            self.num_upgrades: int = 2
            self.current_grid_index: int = 0  # which unit index is selected

            self.generate_upgrades()

    def update(self, delta_time: float):
        pass

    def reset(self):
        self.upgrades_available = []
        self.selected_upgrade = None

        self.generate_upgrades()

    def generate_upgrades(self):
        """
        Generate upgrades to sell. NOTE: currently hard coded.
        """
        # reset existing upgrades
        self.upgrades_available = []

        # TODO - replace with proc gen
        self.upgrades_available = [self._game.data.upgrades["minor_attack"], self._game.data.upgrades["minor_defence"]]

    def calculate_upgrade_cost(self, tier: int):
        """
        Calculate the cost of the upgrade based on the tier of the upgrade.
        """
        tier_multiplier = self._game.data.config["upgrade"]["tier_cost_multiplier"]
        upgrade_cost = self._game.data.config["upgrade"]["cost"]

        # only apply multiplier post tier 1
        if tier > 1:
            mod = tier_multiplier * tier
        else:
            mod = 1

        cost = int(mod * upgrade_cost)

        return cost

    def upgrade_unit(self, unit: Unit):
        """
        Upgrade the unit.
        """
        # can we afford
        id_ = unit.id
        upgrade = self.selected_upgrade
        upgrade_cost = self.calculate_upgrade_cost(upgrade["tier"])

        # pay for the upgrade and execute it
        self._parent_scene.model.amend_gold(-upgrade_cost)  # remove gold cost
        self._parent_scene.model.player_troupe.upgrade_unit(id_, upgrade["type"])

        # clear upgrade option from list
        index = self.upgrades_available.index(self.selected_upgrade)
        self.upgrades_available[index] = None

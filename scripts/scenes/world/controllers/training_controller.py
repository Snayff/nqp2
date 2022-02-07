from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import TrainingState
from scripts.core.debug import Timer

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict, Any
    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["TrainingController"]


class TrainingController(Controller):
    """
    Training game functionality and training only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("TrainingController initialised"):
            super().__init__(game, parent_scene)

            self.upgrades_offered: List[Dict[str, Any]] = []
            self.upgrades_available: Dict[str, bool] = {}  # upgrade.type : is_available


    def update(self, delta_time: float):
        pass


    def reset(self):
        self.upgrades_offered = []
        self.upgrades_available = {}

    def generate_upgrades(self):
        """
        Generate upgrades to sell. NOTE: currently hard coded.
        """
        self.upgrades_offered = [self._game.data.upgrades["minor_attack"], self._game.data.upgrades["minor_defence"]]
        self.upgrades_available = {"minor_attack": True, "minor_defence": True}

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

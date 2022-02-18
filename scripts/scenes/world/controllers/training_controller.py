from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import TrainingState
from scripts.core.debug import Timer

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["TrainingController"]


class TrainingController(Controller):
    """
    Training game functionality and training only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    # TODO:
    #  - draw upgrades on screen
    #  - when transitioning to training state show prompt for selecting upgrades
    #  - input for toggling selection of units and upgrades
    #  - show upgrade details only when upgrade is hovered
    #  - input for selecting upgrade
    #  - when upgrade selected move to units, update local state
    #  - input for navigating units
    #  - input for selecting and applying upgrade to unit
    #  - upgrade confirmation (animation?)

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("TrainingController initialised"):
            super().__init__(game, parent_scene)

            self.upgrades_available: Dict[int, Optional[Any]] = {}  # position: None/upgrade dict
            self.num_upgrades: int = 2

    def update(self, delta_time: float):
        pass

    def reset(self):
        self.upgrades_available = {}

    def generate_upgrades(self):
        """
        Generate upgrades to sell. NOTE: currently hard coded.
        """
        # reset existing upgrades
        self.upgrades_available = {}

        # TODO - replace with proc gen
        upgrades_offered = [self._game.data.upgrades["minor_attack"], self._game.data.upgrades["minor_defence"]]

        # set all positions in dict to None
        for i in range(self.num_upgrades):
            self.upgrades_available[i] = upgrades_offered[i]

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

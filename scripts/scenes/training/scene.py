from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import TrainingState
from scripts.scenes.training.ui import TrainingUI

if TYPE_CHECKING:
    from typing import Dict, List

    from scripts.core.game import Game


__all__ = ["TrainingScene"]


#### TO DO LIST ##########
# TODO - set standard upgrade cost per tier.


class TrainingScene(Scene):
    """
    Handles TrainingScene interactions and consolidates the rendering. TrainingScene is used to upgrade units.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: TrainingUI = TrainingUI(game)
        self.state: TrainingState = TrainingState.CHOOSE_UPGRADE

        self.upgrades_offered: List = []
        self.upgrades_available: Dict[str, bool] = {}  # upgrade.type : is available

        # record duration
        end_time = time.time()
        logging.info(f"TrainingScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def reset(self):
        self.ui = TrainingUI(self.game)
        self.state = TrainingState.CHOOSE_UPGRADE
        self.upgrades_offered = []
        self.upgrades_available = {}

    def generate_upgrades(self):
        """
        Generate upgrades to sell. NOTE: currently hard coded.
        """
        self.upgrades_offered = [self.game.data.upgrades["minor_attack"], self.game.data.upgrades["minor_defence"]]
        self.upgrades_available = {"minor_attack": True, "minor_defence": True}

    def calculate_upgrade_cost(self, tier: int):
        """
        Calculate the cost of the upgrade based on the tier of the upgrade.
        """
        tier_multiplier = self.game.data.config["upgrade"]["tier_cost_multiplier"]
        upgrade_cost = self.game.data.config["upgrade"]["cost"]
        cost = int(((tier_multiplier * tier) * upgrade_cost))

        return cost

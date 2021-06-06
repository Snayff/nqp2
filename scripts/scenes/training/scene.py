from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.training.ui import TrainingUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["TrainingScene"]


class TrainingScene(Scene):
    """
    Handles TrainingScene interactions and consolidates the rendering. TrainingScene is used to upgrade units.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: TrainingUI = TrainingUI(game)

        # record duration
        end_time = time.time()
        logging.info(f"TrainingScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def upgrade_unit(self, id_: int):
        """
        Upgrade the specified unit.
        """
        unit = self.game.memory.player_troupe.units[id_]

        # can we afford
        if unit.upgrade_cost <= self.game.memory.gold:
            # pay gold
            self.game.memory.amend_gold(-unit.upgrade_cost)  # remove gold cost

            # upgrade unit
            unit.upgrade()

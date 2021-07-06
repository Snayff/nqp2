from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.training.ui import TrainingUI

if TYPE_CHECKING:
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

        # record duration
        end_time = time.time()
        logging.info(f"TrainingScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

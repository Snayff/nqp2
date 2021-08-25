from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.unit_data.ui import UnitDataUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["UnitDataScene"]


class UnitDataScene(Scene):
    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.DEV_UNIT_DATA)

        self.ui: UnitDataUI = UnitDataUI(game)

        self.previous_scene_type: SceneType = SceneType.DEV_UNIT_DATA

        # record duration
        end_time = time.time()
        logging.info(f"UnitDataScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def reset(self):
        self.ui = UnitDataUI(self.game)

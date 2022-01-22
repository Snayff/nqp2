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

        super().__init__(game, SceneType.DEV_DATA_EDITOR)

        self.ui: UnitDataUI = UnitDataUI(game, self)

        self.previous_scene_type: SceneType = SceneType.DEV_DATA_EDITOR

        # record duration
        end_time = time.time()
        logging.debug(f"UnitDataScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def draw(self):
        self.ui.draw(self._game.window.display)

    def reset(self):
        self.ui = UnitDataUI(self._game, self)

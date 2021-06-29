from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import time
from scripts.scenes.unit_data.ui import UnitDataUI
from scripts.core.base_classes.scene import Scene

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["UnitDataUI"]


class UnitDataScene(Scene):
    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: UnitDataUI = UnitDataUI(game)

        # record duration
        end_time = time.time()
        logging.info(f"EventScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

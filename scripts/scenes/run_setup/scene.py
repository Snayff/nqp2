from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.run_setup.ui import RunSetupUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["RunSetupScene"]


class RunSetupScene(Scene):
    """
    Handles RunSetupScene interactions and consolidates the rendering. RunSetupScene is used to allow the player to
    determine the conditions of their run.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: RunSetupUI = RunSetupUI(game)

        self.selected_home = ""
        self.selected_ally = ""

        # record duration
        end_time = time.time()
        logging.info(f"RunSetupScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def start_run(self):
        pass
    
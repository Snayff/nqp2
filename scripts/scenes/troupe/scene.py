from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.troupe.ui import TroupeUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["TroupeScene"]


class TroupeScene(Scene):
    """
    Handles TroupeScene interactions and consolidates the rendering. TroupeScene is used to view the troupe
    information.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: TroupeUI = TroupeUI(game)

        self.previous_scene_type: SceneType = SceneType.TROUPE

        # record duration
        end_time = time.time()
        logging.info(f"TroupeScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

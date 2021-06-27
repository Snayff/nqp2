from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.view_troupe.ui import ViewTroupeUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["ViewTroupeScene"]


class ViewTroupeScene(Scene):
    """
    Handles ViewTroupeScene interactions and consolidates the rendering. ViewTroupeScene is used to view the troupe
    information.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: ViewTroupeUI = ViewTroupeUI(game)

        self.previous_scene_type: SceneType = SceneType.VIEW_TROUPE

        # record duration
        end_time = time.time()
        logging.info(f"ViewTroupeScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

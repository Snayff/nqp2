from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from nqp.base_classes.scene import Scene
from nqp.core.constants import SceneType
from nqp.scenes.gallery.ui import GalleryUI

if TYPE_CHECKING:
    from nqp.core.game import Game

__all__ = ["GalleryScene"]


class GalleryScene(Scene):
    """
    Handles Scene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.DEV_GALLERY)

        self.ui: GalleryUI = GalleryUI(game, self)

        self.previous_scene_type: SceneType = SceneType.DEV_GALLERY

        # record duration
        end_time = time.time()
        logging.debug(f"GalleryScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = GalleryUI(self._game, self)

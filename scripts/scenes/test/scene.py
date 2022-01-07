from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.test.ui import TestUI
from scripts.scenes.world.ui import WorldUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["TestScene"]


class TestScene(Scene):
    """
    Handles WorldScene interactions and consolidates the rendering. Draws the underlying map present in most Scenes.
    """

    def __init__(self, game: Game):
        super().__init__(game, SceneType.WORLD)

        self.ui: TestUI = TestUI(game, self)

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = TestUI(self.game, self)

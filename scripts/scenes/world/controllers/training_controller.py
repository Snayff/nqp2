from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.debug import Timer

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["TrainingController"]


class TrainingController(Controller):
    """
    Training game functionality

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("GeneralController initialised"):
            super().__init__(game, parent_scene)

    def update(self, delta_time: float):
        pass



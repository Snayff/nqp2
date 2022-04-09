from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

    from nqp.core.game import Game
    from nqp.scenes.world.scene import WorldScene

__all__ = ["Controller"]


class Controller(ABC):
    """
    Manage game functionality for a specific context

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        self._game = game
        self._parent_scene = parent_scene

    @abstractmethod
    def update(self, delta_time: float):
        pass

    @abstractmethod
    def reset(self):
        pass

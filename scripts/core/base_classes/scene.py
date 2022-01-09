from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI
from scripts.core.constants import SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["Scene"]


class Scene(ABC):
    """
    Handles Scene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game, scene_type: SceneType):
        self.game: Game = game

        self.ui: UI = None  # ignore_type
        self.type: SceneType = scene_type
        self.is_active: bool = False

    @abstractmethod
    def update(self, delta_time: float):
        pass

    @abstractmethod
    def reset(self):
        pass

    def activate(self):
        """
        Activate the Scene. Propagates to the scene's UI.
        """
        self.is_active = True
        self.ui.activate()

    def deactivate(self):
        """
        Deactivate the Scene. Propagates to the scene's UI.
        """
        self.is_active = False
        self.ui.deactivate()

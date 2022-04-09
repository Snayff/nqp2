from __future__ import annotations

from typing import TYPE_CHECKING

from nqp.base_classes.scene import Scene
from nqp.core.constants import SceneType
from nqp.core.debug import Timer
from nqp.scenes.view_troupe.ui import ViewTroupeUI

if TYPE_CHECKING:
    from nqp.core.game import Game

__all__ = ["ViewTroupeScene"]


class ViewTroupeScene(Scene):
    """
    Handles ViewTroupeScene interactions and consolidates the rendering. ViewTroupeScene is used to view the troupe
    information.
    """

    def __init__(self, game: Game):
        with Timer("ViewTroupeScene: initialised"):

            super().__init__(game, SceneType.VIEW_TROUPE)

            self.ui: ViewTroupeUI = ViewTroupeUI(game, self)

            self.previous_scene_type: SceneType = SceneType.VIEW_TROUPE

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = ViewTroupeUI(self._game, self)
        self.previous_scene_type = SceneType.VIEW_TROUPE

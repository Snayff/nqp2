from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.inn.ui import InnUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["InnScene"]


class InnScene(Scene):
    """
    Handles InnScene interactions and consolidates the rendering. InnScene is used to buy units.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.ui: InnUI = InnUI(game)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

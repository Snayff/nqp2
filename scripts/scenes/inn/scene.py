from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.scenes.inn.ui import InnUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["InnScene"]


class InnScene:
    """
    Handles InnScene interactions and consolidates the rendering. InnScene is used to buy units.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: InnUI = InnUI(game)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

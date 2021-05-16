from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.ui.inn import InnUI

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Inn"]


class Inn:
    """
    Handles Inn interactions and consolidates the rendering. Inn is used to buy units.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: InnUI = InnUI(game)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.scenes.training.ui import TrainingUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["Training"]


class Training:
    """
    Handles Training interactions and consolidates the rendering. Training is used to upgrade units.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: TrainingUI = TrainingUI(game)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

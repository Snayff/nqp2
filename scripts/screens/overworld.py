from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.elements.map_manager import MapManager
from scripts.ui.overworld import OverworldUI

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Overworld"]


class Overworld:
    """
    Represents the overworld view and handles related interactions.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.map: MapManager = MapManager(game)

        self.ui = OverworldUI(game)

    def update(self):
        self.ui.update()
        self.map.update()

    def render(self):
        self.map.render(self.game.window.display)
        self.ui.render(self.game.window.display)

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.elements.map_manager import MapManager

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

    def update(self):
        pass

    def render(self):
        self.map.render(self.game.window.display)

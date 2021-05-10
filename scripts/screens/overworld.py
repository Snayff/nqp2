from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.elements.map_manager import MapManager
from scripts.ui.overworld import OverworldUI

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Overworld"]


class Overworld:
    """
    Handles Overworld interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.map: MapManager = MapManager(game)

        self.ui: OverworldUI = OverworldUI(game)

    def update(self):
        self.map.update()
        self.ui.update()

    def render(self):
        self.map.render(self.game.window.display)
        self.ui.render(self.game.window.display)


## TO DO LIST ##
# TODO - implement use of a seed
# TODO - allow number of nodes per row to vary
# TODO - connect nodes across rows randomly
# TODO - output to log results of generation


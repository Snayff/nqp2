from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.scenes.overworld.elements.map_manager import MapManager
from scripts.scenes.overworld.ui import OverworldUI
from scripts.core.base_classes.scene import Scene

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["OverworldScene"]


class OverworldScene(Scene):
    """
    Handles OverworldScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        super().__init__(game)

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
# TODO - connect nodes between rows randomly
# TODO - output to log results of generation

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.overworld.elements.map_manager import MapManager
from scripts.scenes.overworld.ui import OverworldUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["OverworldScene"]


## TO DO LIST ##
# TODO - allow number of nodes per row to vary
# TODO - connect nodes between rows randomly
# TODO - output to log results of generation
# TODO - generate a tilemap and place nodes on that, so it actually looks like a world.
# FIXME - able to select across unconnected nodes
# TODO - generate a boss fight (troupe containing commander) as the only node on the final row


class OverworldScene(Scene):
    """
    Handles OverworldScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.map: MapManager = MapManager(game)

        self.ui: OverworldUI = OverworldUI(game)

        # record duration
        end_time = time.time()
        logging.info(f"OverworldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.map.update()
        self.ui.update()

    def render(self):
        self.map.render(self.game.window.display)
        self.ui.render(self.game.window.display)

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import DEFAULT_IMAGE_SIZE, NodeState, NodeType, OverworldState
from scripts.scenes.overworld.elements.node import Node
from scripts.scenes.overworld.elements.rings import Rings
from scripts.scenes.overworld.ui import OverworldUI

if TYPE_CHECKING:
    from typing import List

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

        self.ui: OverworldUI = OverworldUI(game)

        self.node_container = None

        self.nodes: List[List[Node]] = []
        self.current_node_row: int = 0
        self.state: OverworldState = OverworldState.LOADING

        # record duration
        end_time = time.time()
        logging.info(f"OverworldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)

        for row in self.nodes:
            for node in row:
                node.update(delta_time)

        self.ui.update(delta_time)

    def render(self):
        self.node_container.render(self.game.window.display)
        self.ui.render(self.game.window.display)

    def generate_map(self):
        """
        Create a map of nodes
        """
        centre = self.game.window.centre
        self.node_container = Rings(self.game, centre, 160, 5)
        self.node_container.generate_nodes()

        self.state = OverworldState.READY

    def increment_row(self):
        """
        Increment the row, create a new level if all rows completed.
        """
        self.current_node_row += 1

        # check if we reached the end of the rows
        if self.current_node_row >= len(self.nodes):
            self.increment_level()

    def increment_level(self):
        """
        Increment the level, renewing the map.
        """
        self.state = OverworldState.LOADING

        self.generate_map()

        self.game.memory.level += 1

    def reset(self):
        self.ui = OverworldUI(self.game)

        self.nodes = []
        self.current_node_row = 0
        self.state = OverworldState.LOADING
        self.game.memory.level = 1

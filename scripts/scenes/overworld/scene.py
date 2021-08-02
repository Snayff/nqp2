from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import DEFAULT_IMAGE_SIZE, NodeState, NodeType, OverworldState
from scripts.scenes.overworld.elements.node import Node
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
# TODO - externalise config


class OverworldScene(Scene):
    """
    Handles OverworldScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: OverworldUI = OverworldUI(game)

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
        for row in self.nodes:
            for node in row:
                node.render(self.game.window.display)

        self.ui.render(self.game.window.display)

    def generate_map(self):
        """
        Create a map of nodes
        """

        # example implementations:
        # https://github.com/yurkth/stsmapgen
        # https://github.com/a327ex/blog/issues/47

        # implementation notes:
        # 1. every route must have the same number of nodes.
        # 2. all nodes must be accessible to at least 1 node above and below.
        # 3. connections between nodes must not cross.

        # config
        min_nodes_per_row = 2
        max_nodes_per_row = 4
        depth = 5

        node_types = [NodeType.COMBAT, NodeType.EVENT, NodeType.INN, NodeType.TRAINING, NodeType.UNKNOWN]
        node_weights = [0.5, 0.2, 0.1, 0.1, 0.2]

        nodes = []
        previous_row = []

        # positions
        base_x = 10
        x = base_x
        y = 10

        # generate first row
        # proc number of nodes
        num_nodes = self.game.rng.randint(min_nodes_per_row, max_nodes_per_row)

        # TODO - replace with procedural generation
        # init nodes
        for row_num in range(0, depth):
            row = []
            y = y + DEFAULT_IMAGE_SIZE * 2

            for node_num in range(0, num_nodes):
                # generate node type
                node_type = self.game.rng.choices(node_types, node_weights, k=1)[0]

                # get node icon
                node_icon = self._get_node_icon(node_type)

                # init  node
                node = Node(node_type, [x, y], node_icon)

                # change state as we're in first row
                if row_num == 0:
                    node.state = NodeState.SELECTABLE
                else:
                    # connect to previous row
                    node.connected_previous_row_nodes.append(previous_row[node_num])

                # increment position
                x += DEFAULT_IMAGE_SIZE * 3

                row.append(node)

            # store row
            nodes.append(row)

            # reset x
            x = base_x

            # retain row info
            previous_row = row

        self.nodes = nodes
        self.state = OverworldState.READY
        self.current_node_row = 0

    def pick_unknown_node(self) -> NodeType:
        """
        Randomly pick a node type that isnt Unknown.
        """
        node_types = [NodeType.COMBAT, NodeType.EVENT, NodeType.INN, NodeType.TRAINING]
        node_weights = [0.2, 0.4, 0.1, 0.1]

        node_type = self.game.rng.choices(node_types, node_weights, k=1)[0]

        return node_type

    def _get_node_icon(self, node_type: NodeType) -> pygame.Surface:
        """
        Get the node icon from the node type
        """
        if node_type == NodeType.COMBAT:
            node_icon = self.game.assets.get_image("nodes", "combat")
        elif node_type == NodeType.EVENT:
            node_icon = self.game.assets.get_image("nodes", "event")
        elif node_type == NodeType.INN:
            node_icon = self.game.assets.get_image("nodes", "inn")
        elif node_type == NodeType.TRAINING:
            node_icon = self.game.assets.get_image("nodes", "training")
        else:
            # node_type == NodeType.UNKNOWN
            node_icon = self.game.assets.get_image("nodes", "unknown")

        return node_icon

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

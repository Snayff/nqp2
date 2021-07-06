from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, MapState, NodeState, NodeType
from scripts.scenes.overworld.elements.node import Node

if TYPE_CHECKING:
    from typing import List

    from scripts.core.game import Game

__all__ = ["MapManager"]


class MapManager:
    """
    Manage the nodes on the map
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.nodes: List[List[Node]] = []
        self.active_row = 0

        self.state: MapState = MapState.LOADING

        self.generate_map()

    def update(self, delta_time: float):
        for row in self.nodes:
            for node in row:
                node.update(delta_time)

    def render(self, surface: pygame.Surface):
        for row in self.nodes:
            for node in row:
                node.render(surface)

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
        # node_types = [NodeType.TRAINING]
        # node_weights = [1]
        node_types = [NodeType.COMBAT, NodeType.EVENT, NodeType.INN, NodeType.TRAINING, NodeType.UNKNOWN]
        node_weights = [0.7, 0.2, 10.1, 0.1, 0.2]

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
                node_icon = self.get_node_icon(node_type)

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
        self.state = MapState.READY

    def get_node_icon(self, node_type: NodeType) -> pygame.Surface:
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

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from scripts.elements.node import Node
from scripts.misc.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, NodeState, NodeType

if TYPE_CHECKING:
    from scripts.management.game import Game
    from typing import List

__all__ = ["MapManager"]


class MapManager:
    """
    Manage the nodes on the map
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.nodes: List[List[Node]] = []
        self.current_row = 0

    def update(self):
        for row in self.nodes:
            for node in row:
                node.update()

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
        min_nodes_per_row = 1
        max_nodes_per_row = 4
        depth = 5
        node_types = [NodeType.COMBAT, NodeType.EVENT, NodeType.INN, NodeType.TRAINING]
        node_weights = [0.9, 0.2, 0.1, 0.1]

        nodes = []
        row = []

        # positions
        x = 10
        y = 10

        # generate first row
        # proc number of nodes
        num_nodes = random.randint(min_nodes_per_row, max_nodes_per_row)

        # init node values
        for _ in range(1, num_nodes):
            # generate node type
            node_type = random.choices(node_types, node_weights, k=1)[0]

            # get node icon
            node_icon = self.get_node_icon(node_type)

            # init  node
            node = Node(node_type, [x, y], node_icon)

            # change state as we're in first row
            node.state = NodeState.SELECTABLE

            # increment position
            x += DEFAULT_IMAGE_SIZE * 3

            row.append(node)

        nodes.append(row)

        # TODO - create remaining rows and connect nodes

        self.nodes = nodes

    def get_node_icon(self, node_type: NodeType) -> pygame.Surface:
        """
        Get the node icon from the node type
        """
        if node_type == NodeType.COMBAT:
            node_icon = self.game.assets.get_image(str(ASSET_PATH / "icons/Skills/Skill112.png"))
        elif node_type == NodeType.EVENT:
            node_icon = self.game.assets.get_image(str(ASSET_PATH / "icons/Skills/Skill93.png"))
        elif node_type == NodeType.INN:
            node_icon = self.game.assets.get_image(str(ASSET_PATH / "icons/Skills/Skill84.png"))
        else:
            # node_type == NodeType.TRAINING
            node_icon = self.game.assets.get_image(str(ASSET_PATH / "icons/Skills/Skill15.png"))

        return node_icon




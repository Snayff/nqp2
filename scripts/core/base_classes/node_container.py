from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import Direction, NodeType


from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from scripts.core.game import Game
    from typing import List, Tuple, Dict

__all__ = ["NodeContainer"]


class NodeContainer(ABC):
    def __init__(self, game: Game):
        self.game: Game = game

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass

    @abstractmethod
    def update(self, delta_time: float):
        pass

    @abstractmethod
    def select_next_node(self, direction: Direction):
        pass

    @abstractmethod
    def generate_nodes(self):
        pass

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

    def _get_random_node_type(self, allow_unknown: bool = True) -> NodeType:
        """
        Return a random node type
        """
        node_weights_dict = self.game.data.config["overworld"]["node_weights"]
        node_types = [NodeType.COMBAT, NodeType.EVENT, NodeType.INN, NodeType.TRAINING]

        if allow_unknown:
            node_types.append(NodeType.UNKNOWN)

        node_weights = []
        try:
            for enum_ in node_types:
                name = enum_.name.lower()
                node_weights.append(node_weights_dict[name])

        except KeyError as key_error:
            logging.warning(f"generate_map: Node key not found in config file. Defaults used. err:{key_error}")

            # overwrite with default
            node_weights = []
            for enum_ in node_types:
                node_weights.append(0.1)

        node_type = self.game.rng.choices(node_types, node_weights, k=1)[0]

        return node_type



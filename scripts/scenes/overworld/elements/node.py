from __future__ import annotations

from typing import List

import pygame

from scripts.core.constants import NodeState, NodeType

__all__ = ["Node"]


class Node:
    """
    Represents a possible interaction on the map
    """

    def __init__(self, node_type: NodeType, pos: List[int], icon: pygame.Surface):
        self.type: NodeType = node_type
        self.state: NodeState = NodeState.REACHABLE
        self.connected_previous_row_nodes: List[Node] = []
        self.pos: List[int] = pos
        self.icon: pygame.Surface = icon

    def update(self):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.icon, self.pos)

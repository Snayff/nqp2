from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import NodeType

if TYPE_CHECKING:
    from typing import List


__all__ = ["Node"]


class Node:
    """
    Represents a possible interaction on the map
    """

    def __init__(self, node_type: NodeType, pos: List[int], icon: pygame.Surface):
        self.type: NodeType = node_type
        self.connected_previous_row_nodes: List[Node] = []
        self.pos: List[int] = pos
        self.icon: pygame.Surface = icon

    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.icon, self.pos)

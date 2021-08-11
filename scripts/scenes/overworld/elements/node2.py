from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import NodeState, NodeType

if TYPE_CHECKING:
    from typing import List, Tuple, Union


__all__ = ["Node2"]


class Node2:
    """
    Represents a possible interaction on the map
    """

    def __init__(self, node_type: NodeType, pos: Tuple[Union[int, float], Union[int, float]], icon: pygame.Surface):
        self.type: NodeType = node_type
        self.state: NodeState = NodeState.REACHABLE
        self.pos: Tuple[Union[int, float], Union[int, float]] = pos
        self.icon: pygame.Surface = icon

    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.icon, self.pos)

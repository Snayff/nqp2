from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import NodeState, NodeType

if TYPE_CHECKING:
    from typing import List, Tuple, Union, Optional


__all__ = ["Node2"]


class Node2:
    """
    Represents a possible interaction on the map
    """

    def __init__(self, node_type: NodeType, pos: Tuple[Union[int, float], Union[int, float]], icon: pygame.Surface):
        self.type: NodeType = node_type
        self.pos: Tuple[Union[int, float], Union[int, float]] = pos
        self.icon: pygame.Surface = icon

        self.connected_outer_node: Optional[Node2] = None
        self.connected_inner_node: Optional[Node2] = None

        self.is_selected: bool = False

    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        if self.is_selected:
            radius = (self.icon.get_width() / 2) + 2
            pygame.draw.circle(surface, (255, 255, 255), self.pos, radius)

        surface.blit(self.icon, self.pos)


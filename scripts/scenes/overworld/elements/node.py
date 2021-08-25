from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import NodeType

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union


__all__ = ["Node"]


class Node:
    """
    Represents a possible interaction on the map
    """

    def __init__(self, node_type: NodeType, pos: Tuple[Union[int, float], Union[int, float]], icon: pygame.Surface):
        self.type: NodeType = node_type
        self.pos: Tuple[Union[int, float], Union[int, float]] = pos
        self.icon: pygame.Surface = icon

        self.connected_outer_node: Optional[Node] = None
        self.connected_inner_node: Optional[Node] = None

        self.is_complete: bool = False  # if the player has already completed

    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.icon, self.pos)

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

    def __init__(self, node_type: NodeType, is_type_hidden: bool, pos: Tuple[Union[int, float], Union[int, float]],
    icon: pygame.Surface):
        self.type: NodeType = node_type
        self.is_type_hidden: bool = is_type_hidden
        self.pos: Tuple[Union[int, float], Union[int, float]] = pos
        self.icon: pygame.Surface = icon

        self.connected_outer_node: Optional[Node] = None
        self.connected_inner_node: Optional[Node] = None

        self.is_complete: bool = False  # if the player has already completed

    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.icon, self.pos)

    def complete(self):
        """
        Set the node to complete and update the icon.
        """
        self.is_complete = True

        # create shade
        fill_image = pygame.Surface((self.icon.get_width(), self.icon.get_height()))
        fill_image.fill((134, 135, 138, 100))

        # create copy of sprite
        icon = self.icon.copy()

        # add shade and icon
        icon.blit(fill_image, (0, 0), special_flags=pygame.BLEND_RGB_MAX)

        # update icon
        self.icon = icon

    def reveal_type(self):
        """
        if node type was hidden, reveal it
        """
        if self.is_type_hidden:
            self.is_type_hidden = False

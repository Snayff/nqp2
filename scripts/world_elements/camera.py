import weakref
from typing import Any, Optional, TYPE_CHECKING

import pygame
import snecs
from snecs.typedefs import EntityID

from scripts.core.components import Position
from scripts.core.definitions import PointLike

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Union


class Camera:
    """
    Basic math for getting view of game world

    Attributes:
        zoom: positive numbers "zoom out", negative numbers "zoom in"

    * World units are equal to pixels at zoom level of 0.0

    """

    def __init__(self, size: PointLike):
        self._pos = pygame.Vector2()
        self._size = pygame.Vector2(size)
        self._target_position: Optional[PointLike] = pygame.Vector2()
        self._target_entity: Optional[EntityID] = None
        self.zoom: float = 0.0

    def centre(self, pos: PointLike):
        """
        Immediately centre the camera on a world point

        """
        self._pos.update(pos)

    def move(self, x: int = 0, y: int = 0):
        """
        Immediately move the camera by relative amount

        """
        self._pos.x += x
        self._pos.y += y

    def set_target_position(self, pos: Optional[PointLike]):
        """
        Move camera to position over time. Pass None to clear.

        """
        if pos is None:
            self._target_position = pos
        else:
            self._target_position = pygame.Vector2(pos)

    def set_target_entity(self, entity: Optional[EntityID]):
        """
        Smoothly track a game entity. Pass None to clear.

        """
        self._target_entity = entity

    def get_centre(self) -> pygame.Vector2:
        """
        Get copy of the position

        """
        return pygame.Vector2(self._pos)

    def update(self, delta_time: float):
        """
        Update camera movements

        """
        if self._target_entity:
            pos = snecs.entity_component(self._target_entity, Position)
            self.set_target_position(pos.pos)

        if self._target_position:
            centre = self.get_centre()
            offset = (self._target_position - centre) / 10 * (delta_time * 60)
            self.centre(centre + offset)

    def render_offset(self) -> pygame.Vector2:
        """
        Return vector for drawing offset

        """
        return self._origin() * -1

    def clamp(self, rect: pygame.Rect):
        """
        Move camera so that it is contained in the rect

        Has same behaviour as `pygame.Rect.clamp`

        """
        clamped = self.get_rect().clamp(rect)
        self._pos.update(clamped.center)

    def get_size(self) -> pygame.Vector2:
        """
        Return vector of the size after zoom is applied

        """
        size = self._size + (self._size * self.zoom)
        return pygame.Vector2(round(abs(size[0])), round(abs(size[1])))

    def get_rect(self) -> pygame.Rect:
        """
        Return Pygame Rect representing the visible area of the camera

        """
        size = self.get_size()
        size = round(size.x), round(size.y)
        pos = self._origin()
        return pygame.Rect(pos, size)

    def reset_movement(self):
        """
        Immediately move camera to tracked position

        """
        if self._target_entity:
            pos = snecs.entity_component(self._target_entity, Position)
            self.set_target_position(pos.pos)

        if self._target_position:
            self.centre(self._target_position)

    def _origin(self) -> pygame.Vector2:
        """
        Return vector representing top left corner of the view

        """
        size = self._size + (self._size * self.zoom)
        size.x = abs(size.x)
        size.y = abs(size.y)
        offset = self._pos - (size / 2)
        return pygame.Vector2(round(offset[0]), round(offset[1]))

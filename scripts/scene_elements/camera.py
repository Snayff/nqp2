import weakref
from typing import Any

import pygame

from scripts.core import PointLike


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
        self._target_position = pygame.Vector2()
        self._target_entity: Any = None
        self.zoom: float = 0.0

    def centre(self, pos: PointLike):
        """
        Immediately centre the camera on a world point

        """
        self._pos.x = pos[0]
        self._pos.y = pos[1]

    def move(self, x: int = 0, y: int = 0):
        """
        Immediately move the camera by relative amount

        """
        self._pos.x += x
        self._pos.y += y

    def move_to_position(self, pos: PointLike):
        """
        Move camera to position over time

        """
        self._target_position = pygame.Vector2(pos)

    def follow(self, entity: Any):
        """
        Smoothly track a game entity

        """
        self._target_entity = weakref.ref(entity)

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
            self.move_to_position(self._target_entity.pos)

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
        self._pos.x = clamped.centerx
        self._pos.y = clamped.centery

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

    def _origin(self) -> pygame.Vector2:
        """
        Return vector representing top left corner of the view

        """
        size = self._size + (self._size * self.zoom)
        size.x = abs(size.x)
        size.y = abs(size.y)
        offset = self._pos - (size / 2)
        return pygame.Vector2(round(offset[0]), round(offset[1]))

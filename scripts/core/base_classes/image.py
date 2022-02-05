from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = ["Image"]


class Image(pygame.sprite.Sprite):
    """
    Class to hold visual information for static images
    """

    def __init__(self, *args: pygame.sprite.Group, image: pygame.Surface, pos: Tuple[int, int] = (-1, -1)):
        super().__init__(*args)

        self._image: pygame.Surface = image
        self._pos: Tuple[int, int] = pos

    def draw(self, surface: pygame.Surface):
        """
        Draw the Image to the given surface. If image pos == (-1, -1) does nothing.
        """
        if self.pos == (-1, -1):
            return

        surface.blit(self._image, self._pos)

    def set_pos(self, pos: Tuple[int, int]):
        self._pos = pos

    @property
    def x(self) -> int:
        return self._pos[0]

    @property
    def y(self) -> int:
        return self._pos[1]

    @property
    def pos(self) -> Tuple[int, int]:
        return self._pos

    @property
    def image(self) -> pygame.Surface:
        return self._image

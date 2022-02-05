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

    def __init__(self, *args: pygame.sprite.Group, image: pygame.Surface):
        super().__init__(*args)

        self._image: pygame.Surface = image

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def width(self) -> int:
        return self._image.get_width()

    @property
    def height(self) -> int:
        return self._image.get_height()

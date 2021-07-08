from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from typing import Tuple
    from scripts.core.game import Game

__all__ = ["UIElement"]


class UIElement(ABC):
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], is_selectable: bool = False):
        self.pos: Tuple[int, int] = pos
        self.size: Tuple[int, int] = size
        self.surface: pygame.Surface = pygame.Surface(self.size)

        self.is_selectable: bool = is_selectable
        self.is_selected: bool = False

    @abstractmethod
    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.surface, self.pos)

        if self.is_selected:
            self._draw_selector(surface)

    @abstractmethod
    def rebuild_surface(self):
        pass

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def _draw_selector(self, surface: pygame.Surface):
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (self.x, self.y + self.height + 2),
            (self.x + self.width, self.y + self.height + 2),
        )






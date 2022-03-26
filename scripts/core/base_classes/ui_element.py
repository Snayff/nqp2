from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

from scripts.core import utility

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union
    from scripts.core.game import Game
    from scripts.core.base_classes.animation import Animation

__all__ = ["UIElement"]


class UIElement(ABC):

    def __init__(self, game: Game, pos: Tuple[int, int], is_selectable: bool = False):
        self._game: Game = game
        self.pos: Tuple[int, int] = pos
        self.size: Tuple[int, int] = (0, 0)
        self.surface: pygame.Surface = pygame.Surface(self.size)

        self.is_selectable: bool = is_selectable
        self._was_selectable: bool = is_selectable  # when deactivated keep the original state of selectable
        self._is_selected: bool = False
        self.is_active: bool = True

        self._previously_selected: Animation = self._game.visuals.create_animation("selector", "previously_selected")
        self._selected_selector: Animation = self._game.visuals.create_animation("selector", "selected")
        self._current_selector: Optional[Animation] = None

    @abstractmethod
    def update(self, delta_time: float):
        pass

    def draw(self, surface: pygame.Surface):
        if self.is_active:
            surface.blit(self.surface, self.pos)

            if self._current_selector is not None:
                self._draw_selector(surface)


    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, state: bool):
        self._is_selected = state

        if state:
            self._current_selector = self._selected_selector
        else:
            self._current_selector = None

    @abstractmethod
    def _rebuild_surface(self):
        pass

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def _draw_selector(self, surface: pygame.Surface):
        x = self.pos[0]
        y = self.pos[1] - self.size[1]
        surface.blit(self._current_selector.surface, (x, y))

    def set_active(self, is_active: bool):
        if is_active:
            self.is_active = True
            self.is_selectable = self._was_selectable

        else:
            self.is_active = False
            self._was_selectable = self.is_selectable
            self.is_selectable = False
            self.is_selected = False

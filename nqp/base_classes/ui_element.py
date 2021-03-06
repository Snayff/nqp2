from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from typing import Optional, Tuple

    from nqp.base_classes.animation import Animation
    from nqp.core.game import Game

__all__ = ["UIElement"]


class UIElement(ABC):
    def __init__(self, game: Game, pos: pygame.Vector2, is_selectable: bool = False, tooltip_key: str | None = None):
        self._game: Game = game
        self.pos: pygame.Vector2 = pos
        self.size: pygame.Vector2 = pygame.Vector2(0, 0)
        self.surface: pygame.Surface = pygame.Surface(self.size)
        self.tooltip_key: None | str = tooltip_key

        self.is_selectable: bool = is_selectable
        self._was_selectable: bool = is_selectable  # when deactivated keep the original state of selectable
        self._is_selected: bool = False
        self.is_active: bool = True
        self.was_previously_selected: bool = False
        self._tooltip_counter: float = 0
        self.show_tooltip: bool = False

        self._previously_selected: Animation = self._game.visual.create_animation(
            "selector", "previously_selected", uses_simulation_time=False
        )
        self._selected_selector: Animation = self._game.visual.create_animation(
            "selector", "selected", uses_simulation_time=False
        )
        self._current_selector: Optional[Animation] = None

    def update(self, delta_time: float):
        # update tooltip counter and flag
        if self.is_selected and not self.show_tooltip:
            self._tooltip_counter += delta_time

            if self._tooltip_counter > self._game.data.options["tooltip_delay"]:
                self.show_tooltip = True

    def draw(self, surface: pygame.Surface):
        if self.is_active:
            surface.blit(self.surface, self.pos)

            if self.is_selected and self._current_selector is not None:
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
            self._tooltip_counter = 0
            self.show_tooltip = False

    @abstractmethod
    def _rebuild_surface(self):
        pass

    @property
    def x(self) -> int:
        return int(self.pos.x)

    @property
    def y(self) -> int:
        return int(self.pos.y)

    @property
    def width(self) -> int:
        return int(self.size.x)

    @property
    def height(self) -> int:
        return int(self.size.y)

    def _draw_selector(self, surface: pygame.Surface):
        x = self.x - self._current_selector.image.width
        y = self.y - self.size.y
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

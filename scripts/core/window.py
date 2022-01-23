from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from typing import List, Tuple, Union

    from scripts.core.game import Game

__all__ = ["Window"]


class Window:
    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self._game: Game = game

        self.base_resolution = [640, 360]
        self.scaled_resolution = [1280, 720]

        self.window = pygame.display.set_mode(self.scaled_resolution, 0, 32)
        pygame.display.set_caption("NQP2")

        self.display = pygame.Surface(self.base_resolution)

        self.delta_time = 0.1
        self.frame_start = time.time()

        # record duration
        end_time = time.time()
        logging.debug(f"Window: initialised in {format(end_time - start_time, '.2f')}s.")

    def refresh(self):
        """
        Clear screen.
        """
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))
        pygame.display.update()
        self.display.fill((0, 0, 0))

    def update(self):
        """
        Update internal timer
        """
        self.delta_time = time.time() - self.frame_start
        self.frame_start = time.time()

    @property
    def height(self) -> int:
        return self.base_resolution[1]

    @property
    def width(self) -> int:
        return self.base_resolution[0]

    @property
    def centre(self) -> Tuple[Union[int, float], Union[int, float]]:
        x = self.base_resolution[0] / 2
        y = self.base_resolution[1] / 2

        return x, y

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Window"]


class Window:
    def __init__(self, game: Game):
        self.game: Game = game

        pygame.init()

        self.base_resolution = [640, 360]
        self.scaled_resolution = [1280, 720]

        self.window = pygame.display.set_mode(self.scaled_resolution, 0, 32)
        pygame.display.set_caption("NQP2")

        self.display = pygame.Surface(self.base_resolution)

        self.dt = 0.1
        self.frame_start = time.time()

    def render_frame(self):
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))
        pygame.display.update()
        self.display.fill((0, 0, 0))

        self.dt = time.time() - self.frame_start
        self.frame_start = time.time()

    @property
    def height(self) -> int:
        return self.base_resolution[1]

    @property
    def width(self) -> int:
        return self.base_resolution[0]

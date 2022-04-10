from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from typing import List, Tuple

__all__ = ["Particle"]


class Particle:
    def __init__(self, loc: pygame.Vector2, vel: pygame.Vector2, dur, colour):
        self.loc: pygame.Vector2 = loc
        self.vel: pygame.Vector2 = vel
        self.dur = dur
        self.colour = colour

    def update(self, dt):
        self.loc = pygame.Vector2(self.vel.x * dt, self.vel.y * dt)

        self.dur -= dt
        if self.dur < 0:
            return False
        return True

    def draw(self, surf: pygame.Surface , offset: pygame.Vector2 = pygame.Vector2(0, 0)):
        surf.set_at((int(self.loc.x + offset.x), int(self.loc.y+ offset.y)), self.colour)

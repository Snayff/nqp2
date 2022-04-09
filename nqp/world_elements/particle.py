from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import List, Tuple

__all__ = ["Particle"]


class Particle:
    def __init__(self, loc, vel, dur, colour):
        self.loc = list(loc)
        self.vel = list(vel)
        self.dur = dur
        self.colour = colour

    def update(self, dt):
        self.loc[0] += self.vel[0] * dt
        self.loc[1] += self.vel[1] * dt

        self.dur -= dt
        if self.dur < 0:
            return False
        return True

    def draw(self, surf, offset=(0, 0)):
        surf.set_at((int(self.loc[0] + offset[0]), int(self.loc[1] + offset[1])), self.colour)

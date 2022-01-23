from __future__ import annotations

import logging
import math
import random
from typing import TYPE_CHECKING

from scripts.scene_elements.particle import Particle

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = []


class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_particle_burst(self, loc, colour, count, speed_range=[30, 60], dur_range=[0.2, 0.3]):
        for i in range(count):
            speed = random.random() * (speed_range[1] - speed_range[0]) + speed_range[0]
            dur = random.random() * (dur_range[1] - dur_range[0]) + dur_range[0]
            angle = random.random() * math.pi * 2
            p = Particle(loc, [math.cos(angle) * speed, math.sin(angle) * speed], dur, colour)
            self.particles.append(p)

    def update(self, dt):
        for i, p in sorted(enumerate(self.particles), reverse=True):
            if not p.update(dt):
                self.particles.pop(i)

    def draw(self, surf, offset=(0, 0)):
        for p in self.particles:
            p.draw(surf, offset=offset)

from __future__ import annotations

import logging
import math
import random
from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import Colour
from nqp.world_elements.particle import Particle

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = ["ParticleManager"]


class ParticleManager:
    """
    Class to manage all particles and their functionality, including creating, drawing and deletion.
    """

    def __init__(self):
        self._particles = []

    def _create_particle_burst(
        self,
        position: pygame.Vector2,
        colour: Colour | Tuple[int, int, int],
        count_range: List[int, int],
        speed_range: List[int, int] = None,
        duration_range: List[int, int] = None,
        allow_shade_variations: bool = False,
    ):
        """
        Create a short burst of coloured circles from a target location in a randomised direction.

        Args:
            count_range: the range of how many particles to create.
            speed_range: the range of the speed of the particles movement
            duration_range: the range of how long the particles will last, in seconds.
            allow_shade_variations: whether the colour used can vary slightly from the one given
        """

        # handle mutable defaults
        if duration_range is None:
            duration_range = [0.2, 0.3]
        if speed_range is None:
            speed_range = [30, 60]

        # get random count
        count = random.randint(count_range[0], count_range[1])

        for i in range(count):
            speed = random.random() * (speed_range[1] - speed_range[0]) + speed_range[0]
            dur = random.random() * (duration_range[1] - duration_range[0]) + duration_range[0]
            angle = random.random() * math.pi * 2

            if allow_shade_variations:
                variation = random.randint(-5, 5)
                colour = (colour[0] - variation, colour[1] - variation, colour[2] - variation)

            p = Particle(position, pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed), dur, colour)
            self._particles.append(p)

    def create_blood_spray(self, pos: pygame.Vector2, blood_colour: Tuple[int, int, int] = Colour.BLOOD_RED):
        self._create_particle_burst(pos, blood_colour, [10, 16], allow_shade_variations=True)

    def create_smoke(self, pos: pygame.Vector2):
        self._create_particle_burst(pos, Colour.GREY_SMOKE, [30, 40])

    def update(self, delta_time: float):
        for i, p in sorted(enumerate(self._particles), reverse=True):
            if not p.update(delta_time):
                self._particles.pop(i)

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        for p in self._particles:
            p.draw(surface, offset=offset)

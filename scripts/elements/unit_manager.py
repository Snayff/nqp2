from __future__ import annotations

from typing import TYPE_CHECKING

import pygame


class UnitManager:
    def __init__(self, game):
        self.game = game

        self.units = []

    def add_unit(self, unit):
        self.units.append(unit)

    def update(self):
        for unit in self.units:
            unit.update()

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        for unit in self.units:
            unit.render(surface, shift=offset)

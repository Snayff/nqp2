from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    pass

__all__ = ["UnitManager"]


class UnitManager:
    def __init__(self, game):
        self._game = game

        self.units = []

    def add_unit_to_combat(self, unit):
        unit.reset_for_combat()
        unit.spawn_entities()
        self.units.append(unit)

    def update(self, delta_time: float):
        for unit in self.units:
            unit.update(delta_time)

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        for unit in self.units:
            unit.render(surface, shift=offset)

        # organize entities for layered rendering
        entity_list = []
        for unit in self.units:
            for entity in unit.entities + unit.dead_entities:
                entity_list.append((entity.pos[1] + entity.img.get_height() // 2, len(entity_list), entity))

        entity_list.sort()

        for entity in entity_list:
            entity[2].render(surface, shift=offset)

        for unit in self.units:
            unit.post_render(surface, shift=offset)

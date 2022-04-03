from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.image import Image
from scripts.world_elements.projectile2 import Projectile2

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.core.game import Game
    from snecs.typedefs import EntityID

__all__ = ["ProjectileManager2"]


class ProjectileManager2:
    def __init__(self, game: Game):
        self._game: Game = game
        self.projectiles: List[Projectile2] = []

    def add_projectile(
            self,
            owner: EntityID,
            target: EntityID,
            projectile_data: Dict[str, Union[Image, int]],
            damage: int
    ):
        self.projectiles.append(Projectile2(self._game, owner, target, projectile_data, damage))

    def update(self, delta_time: float):
        for i, projectile in enumerate(self.projectiles):
            projectile.update(delta_time)
            if not projectile.is_active:
                self.projectiles.pop(i)

    def draw(self, surf, offset: pygame.Vector2):
        for projectile in self.projectiles:
            projectile.draw(surf, offset)



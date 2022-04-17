from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.base_classes.image import Image
from nqp.core.constants import DamageType
from nqp.world_elements.projectile import Projectile

if TYPE_CHECKING:
    from typing import Dict, List, Union

    from snecs.typedefs import EntityID

    from nqp.core.game import Game

__all__ = ["ProjectileManager"]


class ProjectileManager:
    def __init__(self, game: Game):
        self._game: Game = game
        self.projectiles: List[Projectile] = []

    def add_projectile(
            self,
            owner: EntityID,
            target: EntityID,
            projectile_data: Dict[str, Union[Image, int]],
            damage: int,
            damage_type: DamageType,
            penetration: int,
            is_crit: bool
    ):
        self.projectiles.append(Projectile(self._game, owner, target, projectile_data, damage, damage_type,
                                           penetration, is_crit))

    def update(self, delta_time: float):
        for i, projectile in enumerate(self.projectiles):
            projectile.update(delta_time)
            if not projectile.is_active:
                self.projectiles.pop(i)

    def draw(self, surf, offset: pygame.Vector2):
        for projectile in self.projectiles:
            projectile.draw(surf, offset)

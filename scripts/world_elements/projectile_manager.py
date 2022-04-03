from typing import List

import pygame

from scripts.world_elements.projectile import Projectile


class ProjectileManager:
    def __init__(self, game):
        self._game = game
        self.projectiles: List[Projectile] = []

    def add_projectile(self, owner, target):
        self.projectiles.append(Projectile(self._game, owner, target))

    def update(self, dt):
        for i, projectile in enumerate(self.projectiles):
            alive = projectile.update(dt)
            if not alive:
                self.projectiles.pop(i)

    def draw(self, surf, offset: pygame.Vector2):
        for projectile in self.projectiles:
            projectile.draw(surf, offset)

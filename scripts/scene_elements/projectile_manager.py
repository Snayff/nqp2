from scripts.scene_elements.projectile import Projectile


class ProjectileManager:
    def __init__(self, game):
        self._game = game
        self.projectiles = []

    def add_projectile(self, owner, target):
        self.projectiles.append(Projectile(self._game, owner, target))

    def update(self, dt):
        for i, projectile in sorted(enumerate(self.projectiles), reverse=True):
            alive = projectile.update(dt)
            if not alive:
                self.projectiles.pop(i)

    def draw(self, surf, offset=(0, 0)):
        for projectile in self.projectiles:
            projectile.draw(surf, offset)

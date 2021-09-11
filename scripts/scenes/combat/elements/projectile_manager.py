from scripts.scenes.combat.elements.projectile import Projectile

class ProjectileManager:
    def __init__(self, game):
        self.game = game
        self.projectiles = []

    def add_projectile(self, owner, target):
        self.projectiles.append(Projectile(self.game, owner, target))

    def update(self, dt):
        for i, projectile in sorted(enumerate(self.projectiles), reverse=True):
            alive = projectile.update(dt)
            if not alive:
                self.projectiles.pop(i)

    def render(self, surf, offset=(0, 0)):
        for projectile in self.projectiles:
            projectile.render(surf, offset)

from scripts.world_elements.hitbox import Hitbox


class Action:
    def __init__(self, game):
        self._game = game
        self.target_type = "free"

    def use(self):
        pass


class Fireball(Action):
    def __init__(self, *args):
        super().__init__(*args)
        self.type = "fireball"
        self.target_type = "free"
        self.damage = 50
        self.radius = 30

    def use(self, location):
        hitbox = Hitbox(self._game.combat.all_entities, "circle", (location, self.radius), self.damage)
        hitbox.apply()


actions = {"fireball": Fireball}

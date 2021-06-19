from scripts.scenes.combat.elements.troupe import Troupe


class EnemyCombatantsGenerator:
    def __init__(self, game):
        self.game = game
        self.enemy_troupe: Troupe = Troupe(game, "enemy")

    def generate(self):
        # lots of temp stuff here for now
        map_size = self.game.combat.terrain.pixel_size
        rng = self.game.rng

        enemy_count = 2

        for i in range(enemy_count):
            # choose a random spot on the right side of the map
            pos = [rng.random() * map_size[0] // 2 + map_size[0] // 2, rng.random() * map_size[1]]

            enemy_type = rng.choice(["spearman", "juggernaut"])
            id_ = self.enemy_troupe.add_unit_from_type(enemy_type)
            unit = self.enemy_troupe.units[id_]
            unit.pos = pos

            self.game.combat.units.add_unit_to_combat(unit)

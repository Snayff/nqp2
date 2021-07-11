from scripts.scenes.combat.elements.troupe import Troupe


class EnemyCombatantsGenerator:
    def __init__(self, game):
        self.game = game
        self.enemy_troupe: Troupe = Troupe(game, "enemy", ["castle"])

    def generate(self):
        # lots of temp stuff here for now
        map_size = self.game.combat.terrain.pixel_size
        rng = self.game.rng

        combat = self.game.combat._get_random_combat()
        num_units = len(combat["units"])

        # generate positions
        positions = []
        for i in range(num_units):
            # choose a random spot on the right side of the map
            while True:
                pos = [rng.random() * map_size[0] // 2 + map_size[0] // 2, rng.random() * map_size[1]]
                if not self.game.combat.terrain.check_tile_solid(pos):
                    break
            positions.append(pos)

        # generate units
        if self.game.debug.debug_mode:
            ids = self.enemy_troupe.debug_init_units()
            ids = ids[:num_units]
        else:

            ids = self.enemy_troupe.generate_units(num_units, unit_types=combat["units"])

        # assign positions and add to combat
        for id_ in ids:
            unit = self.enemy_troupe.units[id_]

            unit.pos = positions.pop(0)
            self.game.combat.units.add_unit_to_combat(unit)

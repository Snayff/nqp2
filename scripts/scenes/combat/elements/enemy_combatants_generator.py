import logging

from scripts.scenes.combat.elements.troupe import Troupe


class EnemyCombatantsGenerator:
    def __init__(self, game):
        self._game = game
        self.enemy_troupe: Troupe = Troupe(game, "enemy", ["castle"])

    def generate(self):
        # lots of temp stuff here for now
        map_size = self._game.combat.terrain.pixel_size
        rng = self._game.rng

        combat = self._game.combat._get_random_combat()
        logging.debug(f"{combat['type']} combat chosen.")
        num_units = len(combat["units"])

        # generate positions
        positions = []
        for i in range(num_units):
            # choose a random spot on the right side of the map
            while True:
                pos = [
                    self._game.window.base_resolution[0] // 4 * 3
                    + rng.random() * (self._game.window.base_resolution[0] // 4),
                    rng.random() * self._game.window.base_resolution[1],
                ]
                if not self._game.combat.terrain.check_tile_solid(pos):
                    break
            positions.append(pos)

        # generate units
        if self._game.debug.debug_mode:
            ids = self.enemy_troupe.debug_init_units()
            ids = ids[:num_units]
        else:

            ids = self.enemy_troupe.generate_specific_units(unit_types=combat["units"])

        # assign positions and add to combat
        for id_ in ids:
            unit = self.enemy_troupe.units[id_]

            unit.pos = positions.pop(0)
            self._game.combat.units.add_unit_to_combat(unit)

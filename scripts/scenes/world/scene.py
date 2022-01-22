from __future__ import annotations

import logging
import time
from typing import Any, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType, WorldState
from scripts.scenes.combat.elements.particles import ParticleManager
from scripts.scenes.combat.elements.projectile_manager import ProjectileManager
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.world.ui import WorldUI

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game

__all__ = ["WorldScene"]


class WorldScene(Scene):
    """
    Handles WorldScene interactions and consolidates the rendering. Draws the underlying map present in most Scenes.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.WORLD)

        self.ui: WorldUI = WorldUI(game, self)

        self.state = WorldState.IDLE
        self.unit_grid: List = []
        self.last_unit_death = None

        # unit selection grid dimensions
        self.grid_size: List[int, int] = [3, 8]  # col, row
        self.grid_cell_size: int = 32
        self.grid_margin: int = 32

        self.projectiles: ProjectileManager = ProjectileManager(self._game)
        self.particles: ParticleManager = ParticleManager()
        self.combat_category: str = "basic"

        # record duration
        end_time = time.time()
        logging.debug(f"WorldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

        # update all troupes
        for troupe in self._game.memory.troupes.values():
            troupe.update(delta_time)

    def activate(self):
        super().activate()

        self._align_unit_pos_to_unit_grid()

        # test
        #self.generate_combat()

    def reset(self):
        self.ui = WorldUI(self._game, self)
        self.unit_grid = []

    def _align_unit_pos_to_unit_grid(self):
        """
        Add player's units to the unit_grid and align their positions.
        """
        self.unit_grid = []

        units = self._game.memory.player_troupe.units.values()
        for unit in units:
            self.unit_grid.append(unit)

        max_rows = self.grid_size[1]
        grid_margin = self.grid_margin
        grid_cell_size = self.grid_cell_size

        for i, unit in enumerate(self.unit_grid):
            x = i // max_rows
            y = i % max_rows
            unit.set_position([grid_margin + x * grid_cell_size, grid_margin + y * grid_cell_size])

    def move_to_new_room(self):
        """
        stub
        """
        # TODO - write method

        # once new room ready
        if self._game.event.roll_for_event():
            self._game.event.load_random_event()
            self._game.activate_scene(SceneType.EVENT)

    def generate_combat(self):
        rng = self._game.rng

        combat = self._get_random_combat()
        logging.debug(f"{combat['type']} combat chosen.")
        num_units = len(combat["units"])

        enemy_troupe = Troupe(self._game, "enemy", [])

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
                if not self.ui.terrain.check_tile_solid(pos):
                    break
            positions.append(pos)

        # generate units
        if self._game.debug.debug_mode:
            ids = enemy_troupe.debug_init_units()
            ids = ids[:num_units]
        else:

            ids = enemy_troupe.generate_specific_units(unit_types=combat["units"])

        # assign positions and add to combat
        for id_ in ids:
            unit = enemy_troupe.units[id_]

            unit.pos = positions.pop(0)

        self._game.memory.add_troupe(enemy_troupe)


    def _get_random_combat(self) -> Dict[str, Any]:
        if len(self._game.data.combats) > 0:
            level = self._game.memory.level
            combats = self._game.data.combats.values()

            # get possible combats
            possible_combats = []
            possible_combats_occur_rates = []
            for combat in combats:
                # ensure only combat for this level or lower and of desired type
                if combat["level_available"] <= level and combat["category"] == self.combat_category:
                    possible_combats.append(combat)
                    occur_rate = self._game.data.get_combat_occur_rate(combat["type"])
                    possible_combats_occur_rates.append(occur_rate)

            combat_ = self._game.rng.choices(possible_combats, possible_combats_occur_rates)[0]
        else:
            combat_ = {}
        return combat_


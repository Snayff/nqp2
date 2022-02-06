from __future__ import annotations

from typing import List, TYPE_CHECKING

from scripts.core import PointLike
from scripts.core.constants import TILE_SIZE
from scripts.core.debug import Timer
from scripts.scene_elements.particle_manager import ParticleManager
from scripts.scene_elements.projectile_manager import ProjectileManager
from scripts.scene_elements.terrain import Terrain

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["WorldModel"]


class WorldModel:
    """
    Manage Terrain and game entities

    * No drawing should be done here
    * Include common operations for game world state

    The model is like a chess set.  Something else (a controller)
    needs to query the state and *ask* the model to make changes.

    The model should be unaware of what combat is, and instead should
    offer an API that combat, or anything else, can change the state
    of the model without actually being aware of how the model works.

    NOTE: There is some overlap in responsibility with the "Memory",
          and future work should clarify what each should handle.

    """

    def __init__(self, game: Game):
        with Timer("WorldModel initialized"):
            self._game = game
            self.tile_size = TILE_SIZE
            self.unit_grid: List = []
            # grid is col, row
            self.grid_size: List[int, int] = [3, 8]
            self.grid_cell_size: int = 32
            self.grid_margin: int = 32
            self.projectiles: ProjectileManager = ProjectileManager(self._game)
            self.particles: ParticleManager = ParticleManager()
            self.terrain: Terrain = Terrain(self._game, "plains")
            self.terrain.generate()
            self.next_terrain: Terrain = Terrain(self._game, "plains")
            self.next_terrain.generate()

    @property
    def boundaries(self):
        return self.terrain.boundaries

    @property
    def next_boundaries(self):
        # TODO: change this if rooms can move to other sides
        return self.next_terrain.boundaries.move(self.boundaries.width, 0)

    @property
    def total_boundaries(self):
        return self.boundaries.union(self.next_boundaries)

    def px_to_loc(self, pos: PointLike):
        """
        Convert map coordinates to tile coordinate

        * NOTE: map units are "pixels"

        """
        return self.terrain.px_to_loc(pos)

    def update(self, delta_time: float):
        self.particles.update(delta_time)
        self.projectiles.update(delta_time)
        for troupe in self._game.memory.troupes.values():
            troupe.update(delta_time)

    def reset(self):
        self.grid_cell_size = 32
        self.grid_margin = 32
        self.grid_size = [3, 8]
        self.particles = ParticleManager()
        self.projectiles = ProjectileManager(self._game)
        self.unit_grid = []

    def swap_terrains(self):
        """
        Swap primary and next terrains

        """
        temp = self.terrain
        self.terrain = self.next_terrain
        self.next_terrain = temp

    def force_idle(self):
        self.align_unit_pos_to_unit_grid()
        for troupe in self._game.memory.troupes.values():
            troupe.set_force_idle(True)

    def align_unit_pos_to_unit_grid(self):
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
            unit.set_position(
                [
                    grid_margin + x * grid_cell_size,
                    grid_margin + y * grid_cell_size,
                ]
            )

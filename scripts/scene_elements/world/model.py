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
    from scripts.scenes.world.scene import WorldScene

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

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("WorldModel initialized"):
            self._game = game
            self._parent_scene = parent_scene

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
        self.particles = ParticleManager()
        self.projectiles = ProjectileManager(self._game)

    def swap_terrains(self):
        """
        Swap primary and next terrains

        """
        temp = self.terrain
        self.terrain = self.next_terrain
        self.next_terrain = temp

    def force_idle(self):
        self._parent_scene.ui.grid.move_units_to_grid()
        for troupe in self._game.memory.troupes.values():
            troupe.set_force_idle(True)

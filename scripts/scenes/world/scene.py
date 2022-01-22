from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType, WorldState
from scripts.scenes.combat.elements.particles import ParticleManager
from scripts.scenes.combat.elements.projectile_manager import ProjectileManager
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

        # record duration
        end_time = time.time()
        logging.debug(f"WorldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

        self._game.memory.player_troupe.update(delta_time)

    def activate(self):
        super().activate()

        self._align_unit_pos_to_unit_grid()

    def reset(self):
        self.ui = WorldUI(self._game, self)

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

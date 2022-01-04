from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import time

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType, WorldState
from scripts.scenes.combat.elements.unit_manager import UnitManager
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
        self.unit_manager: UnitManager = UnitManager(game)  # TODO - overhaul; perhaps merge into World
        self.unit_grid: List = []

        # record duration
        end_time = time.time()
        logging.debug(f"WorldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)
        self.unit_manager.update(delta_time)

    def reset(self):
        self.ui = WorldUI(self.game, self)

        self.add_player_units()
        self.align_unit_pos_to_unit_grid()

    def add_player_units(self):
        """
        Add the player's unit_manager to the combat and unit_grid
        """
        units = list(self.game.memory.player_troupe.units.values())
        for i, unit in enumerate(units, 1):
            self.unit_grid.append(unit)
            self.unit_manager.add_unit_to_combat(unit)

    def align_unit_pos_to_unit_grid(self):
        for i, unit in enumerate(self.unit_grid):
            x = i // 8
            y = i % 8
            unit.set_position([32 + x * 32, 32 + y * 32])


    def get_all_entities(self):
        entities = []
        for unit in self.unit_manager.units:
            entities += unit.entities
        return entities

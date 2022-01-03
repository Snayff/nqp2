from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import time

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType, WorldState
from scripts.scenes.combat.elements.unit_manager import UnitManager
from scripts.scenes.world.ui import WorldUI

if TYPE_CHECKING:
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
        self.units: UnitManager = UnitManager(game)  # TODO - overhaul; perhaps merge into World

        # record duration
        end_time = time.time()
        logging.debug(f"WorldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = WorldUI(self.game, self)

        # TODO - add all player units to grid, in set position (that persists)
        unit = list(self.game.memory.player_troupe.units.values())[0]
        unit.pos = [100, 100]
        self.units.add_unit_to_combat(unit)

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.node_container import NodeContainer
from scripts.core.base_classes.scene import Scene
from scripts.core.constants import DAYS_UNTIL_BOSS, OverworldState, SceneType
from scripts.scenes.overworld.elements.rings import Rings
from scripts.scenes.overworld.ui import OverworldUI

if TYPE_CHECKING:
    from typing import List, Optional

    from scripts.core.game import Game

__all__ = ["OverworldScene"]


class OverworldScene(Scene):
    """
    Handles OverworldScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.OVERWORLD)

        self.ui: OverworldUI = OverworldUI(game)

        self.node_container: Optional[NodeContainer] = None
        self.state: OverworldState = OverworldState.LOADING

        # record duration
        end_time = time.time()
        logging.debug(f"OverworldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)

        self.node_container.update(delta_time)

        self.ui.update(delta_time)

    def render(self):
        self.node_container.render(self.game.window.display)
        self.ui.render(self.game.window.display)

    def generate_map(self):
        """
        Create a map of nodes
        """
        centre = self.game.window.centre
        self.node_container = Rings(self.game, centre, 160, 5)
        self.node_container.generate_nodes()

        self.state = OverworldState.READY

    def increment_level(self):
        """
        Increment the level, renewing the map.
        """
        self.state = OverworldState.LOADING

        self.generate_map()

        self.game.memory.level += 1
        self.game.memory.generate_level_boss()

    def reset(self):
        """
        Reset values to initial state. Does not overwrite the map.
        """
        self.ui = OverworldUI(self.game)

        self.state = OverworldState.LOADING
        self.game.memory.level = 1
        self.game.memory.generate_level_boss()
        self.game.memory.days_until_boss = DAYS_UNTIL_BOSS
        self.node_container = None

    def pay_move_cost(self):
        """
        Reduce rations to move. Apply injuries if not enough rations.
        """
        rations = self.game.memory.amend_rations(-1)

        if rations <= 0:
            # TODO - add injury allocation
            pass

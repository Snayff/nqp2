from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.combat.elements.commander import Commander
from scripts.scenes.run_setup.ui import RunSetupUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["RunSetupScene"]


######### TO DO LIST ###############
# TODO - add option to create a custom commander. Allow reuse of previous custom commander.


class RunSetupScene(Scene):
    """
    Handles RunSetupScene interactions and consolidates the rendering. RunSetupScene is used to allow the player to
    determine the conditions of their run.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: RunSetupUI = RunSetupUI(game)

        self.selected_commander: str = list(self.game.data.commanders)[0]  # set to first commander
        self.selected_seed: int = int(datetime.now().strftime("%Y%m%d%H%M%S"))

        # record duration
        end_time = time.time()
        logging.info(f"RunSetupScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def start_run(self):
        # set the seed
        self.game.rng.set_seed(self.selected_seed)

        # register commander values
        commander = self.game.data.commanders[self.selected_commander]
        self.game.memory.player_troupe.allies = commander["allies"]
        self.game.memory.commander = Commander(self.game, commander["type"])
        self.game.memory.game = commander["starting_gold"]

        logging.info(f"Player chose {self.selected_commander} as their commander.")

        # prep player troupe
        player_troupe = self.game.memory.player_troupe
        if self.game.debug.debug_mode:
            player_troupe.debug_init_units()
        else:
            player_troupe.generate_units(3, [1])

        logging.info(f"Run starting now!")

        # change scene
        self.game.change_scene(SceneType.OVERWORLD)

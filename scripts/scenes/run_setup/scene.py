from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.run_setup.ui import RunSetupUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["RunSetupScene"]


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
        self.selected_home: str = ""
        self.selected_ally: str = ""
        self.selected_seed: int = int(datetime.now().strftime("%Y%m%d%H%M%S"))

        # record duration
        end_time = time.time()
        logging.info(f"RunSetupScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def start_run(self):
        # set the seed
        self.game.rng.set_seed(self.selected_seed)

        # set the home and ally
        self.game.memory.player_troupe.home = self.selected_home
        self.game.memory.player_troupe.allies.append(self.selected_ally)

        logging.info(f"Player chose {self.selected_home} as their home and {self.selected_ally} as their ally.")

        # prep player troupe
        player_troupe = self.game.memory.player_troupe
        if self.game.debug.debug_mode:
            player_troupe.debug_init_units()
        else:
            player_troupe.generate_units(3, [1])

        logging.info(f"Run starting now!")

        # change scene
        self.game.change_scene(SceneType.OVERWORLD)

    @property
    def ready_to_start(self) -> bool:
        """
        Checks conditions are met to begin
        """
        if self.selected_home != "" and self.selected_ally != "":
            return True
        else:
            return False

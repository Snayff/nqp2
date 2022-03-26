from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.core.debug import Timer
from scripts.scene_elements.commander import Commander
from scripts.scene_elements.troupe import Troupe
from scripts.scenes.run_setup.ui import RunSetupUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["RunSetupScene"]


class RunSetupScene(Scene):
    """
    Handles RunSetupScene interactions and consolidates the rendering.
    RunSetupScene is used to allow the player to determine the conditions of their run.
    """

    def __init__(self, game: Game):
        with Timer("Run Setup Scene initialised"):

            super().__init__(game, SceneType.RUN_SETUP)

            self.ui: RunSetupUI = RunSetupUI(game, self)

            self.selected_commander: str = list(self._game.data.commanders)[0]  # set to first commander
            self.selected_seed: int = int(datetime.now().strftime("%Y%m%d%H%M%S"))

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def start_run(self):
        # set the seed
        self._game.rng.set_seed(self.selected_seed)

        # create commander
        commander = self._game.data.commanders[self.selected_commander]
        self._game.memory.commander = Commander(self._game, commander["type"])

        # create player troupe
        troupe = Troupe(self._game, "player", commander["allies"])

        # register commander values
        starting_values = self._game.data.config["starting_values"]
        gold = starting_values["gold"] + commander["gold"]
        rations = starting_values["rations"] + commander["rations"]
        morale = starting_values["morale"] + commander["morale"]
        charisma = starting_values["charisma"] + commander["charisma"]
        leadership = starting_values["leadership"] + commander["leadership"]

        # prep player troupe
        if self._game.debug.debug_mode:
            troupe.debug_init_units()
        else:
            troupe.generate_specific_units(commander["starting_units"])

        # pass starting values to memory
        self._game.memory.initialise_run(troupe, gold, rations, morale, charisma, leadership)

        logging.info(f"Player chose {self.selected_commander} as their commander. Run starting now!")

        # change scene
        self._game.change_scene(SceneType.WORLD)

    def reset(self):
        """
        Reset to clean state.
        """
        self.ui = RunSetupUI(self._game, self)
        self.selected_commander = list(self._game.data.commanders)[0]  # set to first commander
        self.selected_seed = int(datetime.now().strftime("%Y%m%d%H%M%S"))

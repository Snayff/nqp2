from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.combat.elements.commander import Commander
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.run_setup.ui import RunSetupUI

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

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

        super().__init__(game, SceneType.RUN_SETUP)

        self.ui: RunSetupUI = RunSetupUI(game, self)

        self.selected_commander: str = list(self._game.data.commanders)[0]  # set to first commander
        self.selected_seed: int = int(datetime.now().strftime("%Y%m%d%H%M%S"))

        # record duration
        end_time = time.time()
        logging.debug(f"RunSetupScene: initialised in {format(end_time - start_time, '.2f')}s.")

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
        self._game.memory.add_troupe(troupe)

        # register commander values
        starting_values = self._game.data.config["starting_values"]
        self._game.memory.amend_gold(starting_values["gold"] + commander["gold"])
        self._game.memory.amend_rations(starting_values["rations"] + commander["rations"])
        self._game.memory.amend_morale(starting_values["morale"] + commander["morale"])
        self._game.memory.amend_charisma(starting_values["charisma"] + commander["charisma"])
        self._game.memory.amend_leadership(starting_values["leadership"] + commander["leadership"])

        logging.info(f"Player chose {self.selected_commander} as their commander.")

        # prep player troupe
        player_troupe = self._game.memory.player_troupe
        if self._game.debug.debug_mode:
            player_troupe.debug_init_units()
        else:
            player_troupe.generate_specific_units(commander["starting_units"])

        logging.info(f"Run starting now!")

        # change scene
        self._game.change_scene(SceneType.WORLD)
        self._game.add_scene(SceneType.EVENT, False)

    def reset(self):
        """
        Reset to clean state.
        """
        self.ui = RunSetupUI(self._game, self)
        self.selected_commander = list(self._game.data.commanders)[0]  # set to first commander
        self.selected_seed = int(datetime.now().strftime("%Y%m%d%H%M%S"))

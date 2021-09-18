from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.combat.elements.commander import Commander
from scripts.scenes.main_menu.ui import MainMenuUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["MainMenuScene"]


######### TO DO LIST ###############


class MainMenuScene(Scene):
    """
    Handles MainMenuScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.MAIN_MENU)

        self.ui: MainMenuUI = MainMenuUI(game)

        # record duration
        end_time = time.time()
        logging.debug(f"MainMenuScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def reset(self):
        self.ui = MainMenuUI(self.game)

    def new_game(self):
        """
        Prep the game for a new, fresh game and move to run setup scene.
        """
        self.game.change_scene(SceneType.RUN_SETUP)

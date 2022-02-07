from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.core.debug import Timer
from scripts.scene_elements.world.model import WorldModel
from scripts.scenes.world.controllers.combat_controller import CombatController
from scripts.scenes.world.controllers.training_controller import TrainingController
from scripts.scenes.world.ui import WorldUI

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game

__all__ = ["WorldScene"]


class WorldScene(Scene):
    """
    The WorldScene works differently to other Scenes and is composed of a Model, UI and Controller. There are several
    different controllers, 1 per "room".

    * Model is data
    * Controller is logic
    * UI is player input to logic and display
    * This Scene is the container for the above.
    """

    def __init__(self, game: Game):
        with Timer("WorldScene initialised"):
            super().__init__(game, SceneType.WORLD)
            self.model: WorldModel = WorldModel(game, self)
            self.ui: WorldUI = WorldUI(game, self)
            self.combat: CombatController = CombatController(game, self)
            self.training: TrainingController = TrainingController(game, self)

    def update(self, delta_time: float):
        mod_delta_time = self.model.game_speed * delta_time

        self.model.update(mod_delta_time)
        self.combat.update(mod_delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = WorldUI(self._game, self)

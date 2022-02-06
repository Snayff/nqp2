from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.core.debug import Timer
from scripts.scene_elements.world.model import WorldModel
from scripts.scenes.world.combat import CombatController
from scripts.scenes.world.ui import WorldUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["WorldScene"]


class WorldScene(Scene):
    """
    The WorldScene works differently to other Scenes and is composed of a Model, UI and Controller. The Model holds
    the data and logic, the Controller handles the changes in state and the UI handles display and input.

    Relationships between the elements are:
    Controller <-> Model
    Model <-> UI
    UI -> Controller
    """

    def __init__(self, game: Game):
        with Timer("WorldScene initialised"):
            super().__init__(game, SceneType.WORLD)
            self.model: WorldModel = WorldModel(game, self)
            self.controller = CombatController(game, self.model)
            self.ui: WorldUI = WorldUI(game, self.model, self.controller)

    def update(self, delta_time: float):
        mod_delta_time = self._game.memory.game_speed * delta_time
        self.model.update(mod_delta_time)
        self.controller.update(mod_delta_time)
        self.ui.update(delta_time)

    def reset(self):
        self.ui = WorldUI(self._game, self.model, self.controller)

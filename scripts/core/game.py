from __future__ import annotations

from scripts.core.assets import Assets
from scripts.core.constants import GameState, SceneType
from scripts.core.input import Input
from scripts.core.memory import Memory
from scripts.core.window import Window
from scripts.scenes.combat.scene import CombatScene
from scripts.scenes.event.scene import EventScene
from scripts.scenes.inn.scene import InnScene
from scripts.scenes.overworld.scene import OverworldScene
from scripts.scenes.training.scene import TrainingScene

__all__ = ["Game"]


class Game:
    def __init__(self):

        # managers
        self.window = Window(self)
        self.input = Input(self)
        self.memory = Memory(self)
        self.assets = Assets(self)

        # scenes
        self.combat: CombatScene = CombatScene(self)
        self.overworld: OverworldScene = OverworldScene(self)
        self.event: EventScene = EventScene(self)
        self.training: TrainingScene = TrainingScene(self)
        self.inn: InnScene = InnScene(self)

        # point this to whatever scene is active
        #self.combat.begin_combat()
        self.active_scene = self.overworld

        self.state: GameState = GameState.PLAYING

    def update(self):
        self.input.update()
        self.active_scene.update()

    def render(self):
        self.window.render_frame()
        self.active_scene.render()

    def run(self):
        self.update()
        self.render()

    def quit(self):
        self.state = GameState.EXITING

    def change_scene(self, scene: SceneType):
        """
        Change the active scene
        """
        if scene == SceneType.COMBAT:
            self.combat.begin_combat()
            self.active_scene = self.combat
        elif scene == SceneType.TRAINING:
            # TODO - add TrainingScene
            pass
        elif scene == SceneType.INN:
            # TODO - add InnScene
            pass
        elif scene == SceneType.EVENT:
            self.active_scene = self.event
        elif scene == SceneType.OVERWORLD:
            self.active_scene = self.overworld
        elif scene == SceneType.MAIN_MENU:
            # TODO - add main menu
            pass

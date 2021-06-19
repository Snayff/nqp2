from __future__ import annotations

import logging
import time

import pygame

from scripts.core import debug, utility
from scripts.core.assets import Assets
from scripts.core.constants import GameState, SceneType
from scripts.core.data import Data
from scripts.core.input import Input
from scripts.core.memory import Memory
from scripts.core.window import Window
from scripts.scenes.combat.scene import CombatScene
from scripts.scenes.event.scene import EventScene
from scripts.scenes.inn.scene import InnScene
from scripts.scenes.overworld.scene import OverworldScene
from scripts.scenes.reward.scene import RewardScene
from scripts.scenes.training.scene import TrainingScene

__all__ = ["Game"]

from scripts.scenes.troupe.scene import TroupeScene


class Game:
    def __init__(self):
        # start timer
        start_time = time.time()

        # init libraries
        pygame.init()

        # managers
        self.window: Window = Window(self)
        self.data: Data = Data(self)
        self.memory: Memory = Memory(self)
        self.assets: Assets = Assets(self)
        self.input: Input = Input(self)

        # scenes
        self.combat: CombatScene = CombatScene(self)
        self.reward: RewardScene = RewardScene(self)
        self.overworld: OverworldScene = OverworldScene(self)
        self.event: EventScene = EventScene(self)
        self.training: TrainingScene = TrainingScene(self)
        self.inn: InnScene = InnScene(self)
        self.troupe: TroupeScene = TroupeScene(self)

        # point this to whatever scene is active
        self.active_scene = self.overworld

        self.state: GameState = GameState.PLAYING

        self.master_clock = 0

        # FOR USE DURING TESTING
        self.memory.player_troupe.debug_init_units()

        # record duration
        end_time = time.time()
        logging.info(f"Game initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.master_clock += self.window.dt
        self.input.update()
        self.active_scene.update()
        debug.update()

    def render(self):
        self.window.render_frame()
        self.active_scene.render()

    def run(self):
        self.update()
        self.render()

    def quit(self):
        self.state = GameState.EXITING

    def change_scene(self, scene_type: SceneType):
        """
        Change the active scene
        """
        if scene_type == SceneType.COMBAT:
            self.combat.begin_combat()
            self.active_scene = self.combat

        elif scene_type == SceneType.TRAINING:
            self.active_scene = self.training

        elif scene_type == SceneType.INN:
            self.active_scene = self.inn

        elif scene_type == SceneType.EVENT:
            self.active_scene = self.event

        elif scene_type == SceneType.OVERWORLD:
            self.active_scene = self.overworld

        elif scene_type == SceneType.MAIN_MENU:
            # TODO - add main menu
            pass

        elif scene_type == SceneType.TROUPE:
            self.troupe.previous_scene_type = utility.scene_to_scene_type(self.active_scene)
            self.active_scene = self.troupe

        elif scene_type == SceneType.REWARD:
            self.reward.generate_reward()
            self.active_scene = self.reward

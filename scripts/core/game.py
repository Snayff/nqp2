from __future__ import annotations

import logging
import time

import pygame as pygame

from scripts.core import debug, utility
from scripts.core.assets import Assets
from scripts.core.constants import GameState, SceneType
from scripts.core.data import Data
from scripts.core.debug import Debugger
from scripts.core.input import Input
from scripts.core.memory import Memory
from scripts.core.rng import RNG
from scripts.core.window import Window
from scripts.scenes.combat.scene import CombatScene
from scripts.scenes.event.scene import EventScene
from scripts.scenes.inn.scene import InnScene
from scripts.scenes.overworld.scene import OverworldScene
from scripts.scenes.post_combat.scene import PostCombatScene
from scripts.scenes.run_setup.scene import RunSetupScene
from scripts.scenes.training.scene import TrainingScene
from scripts.scenes.unit_data.scene import UnitDataScene
from scripts.scenes.view_troupe.scene import ViewTroupeScene


__all__ = ["Game"]


############ TO DO LIST ############
# TODO - standardise use of id / id_
# TODO - add data checking to ensure ids are unique and values are as expected


class Game:
    def __init__(self):
        # start timer
        start_time = time.time()

        # init libraries
        pygame.init()

        # managers
        self.debug: Debugger = Debugger(self)
        self.window: Window = Window(self)
        self.data: Data = Data(self)
        self.memory: Memory = Memory(self)
        self.assets: Assets = Assets(self)
        self.input: Input = Input(self)
        self.rng: RNG = RNG(self)

        # scenes
        self.combat: CombatScene = CombatScene(self)
        self.post_combat: PostCombatScene = PostCombatScene(self)
        self.overworld: OverworldScene = OverworldScene(self)
        self.event: EventScene = EventScene(self)
        self.training: TrainingScene = TrainingScene(self)
        self.inn: InnScene = InnScene(self)
        self.troupe: ViewTroupeScene = ViewTroupeScene(self)
        self.run_setup: RunSetupScene = RunSetupScene(self)

        # dev scenes
        self.dev_unit_data: UnitDataScene = UnitDataScene(self)

        # point this to whatever scene is active
        self.active_scene = self.run_setup
        self.run_setup.ui.rebuild_ui()

        self.state: GameState = GameState.PLAYING

        self.master_clock = 0

        # record duration
        end_time = time.time()
        logging.info(f"Game initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        delta_time = self.window.dt

        self.master_clock += delta_time

        self.input.update(delta_time)
        self.active_scene.update(delta_time)
        self.debug.update(delta_time)

    def render(self):
        self.window.render_frame()
        self.active_scene.render()
        self.debug.render()  # always last so it is on top

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

        elif scene_type == SceneType.POST_COMBAT:
            self.post_combat.generate_reward()
            self.post_combat.ui.rebuild_ui()
            self.active_scene = self.post_combat

        elif scene_type == SceneType.TRAINING:
            self.training.ui.rebuild_ui()
            self.active_scene = self.training

        elif scene_type == SceneType.INN:
            self.inn.generate_sale_options()
            self.inn.ui.rebuild_ui()
            self.active_scene = self.inn

        elif scene_type == SceneType.EVENT:
            self.event.ui.rebuild_ui()
            self.active_scene = self.event

        elif scene_type == SceneType.OVERWORLD:
            if not self.overworld.has_generated_map:
                self.overworld.generate_map()

            self.active_scene = self.overworld

        elif scene_type == SceneType.MAIN_MENU:
            # TODO - add main menu
            pass

        elif scene_type == SceneType.VIEW_TROUPE:
            self.troupe.previous_scene_type = utility.scene_to_scene_type(self.active_scene)
            self.troupe.ui.rebuild_ui()
            self.active_scene = self.troupe

        elif scene_type == SceneType.RUN_SETUP:
            self.run_setup.ui.rebuild_ui()
            self.active_scene = self.run_setup

        elif scene_type == SceneType.DEV_UNIT_DATA:
            self.dev_unit_data.previous_scene_type = utility.scene_to_scene_type(self.active_scene)
            self.active_scene = self.dev_unit_data

        logging.info(f"Active scene changed to {scene_type.name}.")

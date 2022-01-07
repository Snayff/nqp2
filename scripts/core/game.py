from __future__ import annotations

import logging
import time
from typing import List, Optional

import pygame as pygame

from scripts.core import utility
from scripts.core.assets import Assets
from scripts.core.base_classes.scene import Scene
from scripts.core.constants import GameState, SceneType
from scripts.core.data import Data
from scripts.core.debug import Debugger
from scripts.core.input import Input
from scripts.core.memory import Memory
from scripts.core.rng import RNG
from scripts.core.window import Window
from scripts.scenes.combat.scene import CombatScene
from scripts.scenes.event.scene import EventScene
from scripts.scenes.gallery.scene import GalleryScene
from scripts.scenes.inn.scene import InnScene
from scripts.scenes.main_menu.scene import MainMenuScene
from scripts.scenes.overworld.scene import OverworldScene
from scripts.scenes.post_combat.scene import PostCombatScene
from scripts.scenes.run_setup.scene import RunSetupScene
from scripts.scenes.test.scene import TestScene
from scripts.scenes.training.scene import TrainingScene
from scripts.scenes.unit_data.scene import UnitDataScene
from scripts.scenes.view_troupe.scene import ViewTroupeScene
from scripts.scenes.world.scene import WorldScene

__all__ = ["Game"]


############ TO DO LIST ############


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
        self.main_menu: MainMenuScene = MainMenuScene(self)
        self.run_setup: RunSetupScene = RunSetupScene(self)
        self.overworld: OverworldScene = OverworldScene(self)
        self.combat: CombatScene = CombatScene(self)
        self.post_combat: PostCombatScene = PostCombatScene(self)
        self.event: EventScene = EventScene(self)
        self.training: TrainingScene = TrainingScene(self)
        self.inn: InnScene = InnScene(self)
        self.troupe: ViewTroupeScene = ViewTroupeScene(self)
        self.world: WorldScene = WorldScene(self)
        self.test = TestScene(self)

        # dev scenes
        self.dev_unit_data: UnitDataScene = UnitDataScene(self)
        self.dev_gallery: GalleryScene = GalleryScene(self)

        self.active_scenes: List[Scene] = []

        self.state: GameState = GameState.PLAYING

        self.master_clock = 0

        # activate main menu
        self.activate_scene(SceneType.MAIN_MENU)

        # record duration
        end_time = time.time()
        logging.info(f"Game initialised in {format(end_time - start_time, '.2f')}s.")

    def _update(self):
        # update delta time first
        self.window.update()
        delta_time = self.window.delta_time

        self.master_clock += delta_time

        self.input.update(delta_time)
        for scene in self.active_scenes:
            scene.update(delta_time)
        self.debug.update(delta_time)

    def _render(self):
        # always refresh first
        self.window.refresh()

        surface = self.window.display
        for scene in self.active_scenes:
            # handle those scenes that still have render methods
            if scene in (self.combat, self.overworld):
                scene.render(surface)
            scene.ui.render(surface)
        self.debug.render()  # always last so it is on top

    def run(self):
        self._update()
        self._process_input()
        self._render()

    def _process_input(self):
        delta_time = self.window.delta_time

        # process input in each scene, from the top of the stack, until a scene blocks input
        for scene in reversed(self.active_scenes):
            scene.ui.process_input(delta_time)
            if scene.ui.block_onward_input:
                break

        self.input.reset()

    def quit(self):
        self.state = GameState.EXITING

    def activate_scene(self, scene_type: SceneType):
        """
        Add a scene to the scene stack
        """
        # reset input to ensure no input carries over between scenes
        self.input.reset()

        scene = self._scene_type_to_scene(scene_type)

        # reset and rebuild scene
        scene.reset()
        scene.ui.rebuild_ui()

        # add scene to active list

        self.active_scenes.append(scene)

    def deactivate_scene(self, scene_type: SceneType):
        """
        Remove a scene from the scene stack
        """
        # reset input to ensure no input carries over between scenes
        self.input.reset()

        scene = self._scene_type_to_scene(scene_type)
        self.active_scenes.remove(scene)

    def _scene_type_to_scene(self, scene_type: SceneType) -> Optional[Scene]:
        if scene_type == SceneType.MAIN_MENU:
            scene = self.main_menu

        elif scene_type == SceneType.RUN_SETUP:
            scene = self.run_setup

        elif scene_type == SceneType.OVERWORLD:
            scene = self.overworld

        elif scene_type == SceneType.COMBAT:
            scene = self.combat

        elif scene_type == SceneType.BOSS_COMBAT:
            scene = self.combat

        elif scene_type == SceneType.POST_COMBAT:
            scene = self.post_combat

        elif scene_type == SceneType.TRAINING:
            scene = self.training

        elif scene_type == SceneType.INN:
            scene = self.inn

        elif scene_type == SceneType.EVENT:
            scene = self.event

        elif scene_type == SceneType.VIEW_TROUPE:
            scene = self.troupe

        elif scene_type == SceneType.WORLD:
            scene = self.world

        else:
            scene = None
            logging.error(f"_scene_type_to_scene: No matching SceneType found. Given [{scene_type}].")

        return scene

    def change_scene(self, scene_type: SceneType):
        """
        Deactivate all active scenes and activate the given scene.
        """
        for scene in self.active_scenes:
            self.deactivate_scene(scene.type)

        self.activate_scene(scene_type)

    def old_change_scene(self, scene_type: SceneType):
        """
        Change the active scene. N.B. not used for switching to dev scenes.
        """
        # reset exiting scene if not overworld
        if self.active_scene is not self.overworld:
            if hasattr(self.active_scene, "reset"):
                self.active_scene.reset()

        # reset input to ensure no input carries over between scenes
        self.input.reset()

        # change scene and take scene specific action
        if scene_type == SceneType.MAIN_MENU:
            self.active_scene = self.main_menu

        elif scene_type == SceneType.RUN_SETUP:
            self.active_scene = self.run_setup

        elif scene_type == SceneType.OVERWORLD:
            self.active_scene = self.overworld
            self.overworld.node_container.is_travel_paused = False

        elif scene_type == SceneType.COMBAT:
            self.combat.generate_combat()
            self.active_scene = self.combat

        elif scene_type == SceneType.BOSS_COMBAT:
            self.combat.combat_category = "boss"
            self.combat.generate_combat()
            self.active_scene = self.combat

        elif scene_type == SceneType.POST_COMBAT:
            self.post_combat.generate_reward()
            self.active_scene = self.post_combat

        elif scene_type == SceneType.TRAINING:
            self.training.generate_upgrades()
            self.active_scene = self.training

        elif scene_type == SceneType.INN:
            self.inn.generate_sale_options()
            self.active_scene = self.inn

        elif scene_type == SceneType.EVENT:
            self.event.load_random_event()
            self.active_scene = self.event

        elif scene_type == SceneType.VIEW_TROUPE:
            self.troupe.previous_scene_type = utility.scene_to_scene_type(self.active_scene)
            self.active_scene = self.troupe

        # rebuild ui
        if hasattr(self.active_scene, "ui"):
            if hasattr(self.active_scene.ui, "rebuild_ui"):
                self.active_scene.ui.rebuild_ui()

        logging.info(f"Active scene changed to {scene_type.name}.")

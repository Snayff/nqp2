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
from scripts.scenes.post_combat.scene import PostCombatScene
from scripts.scenes.run_setup.scene import RunSetupScene
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
        pygame.joystick.init()

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
        self.combat: CombatScene = CombatScene(self)
        self.post_combat: PostCombatScene = PostCombatScene(self)
        self.event: EventScene = EventScene(self)
        self.training: TrainingScene = TrainingScene(self)
        self.inn: InnScene = InnScene(self)
        self.troupe: ViewTroupeScene = ViewTroupeScene(self)
        self.world: WorldScene = WorldScene(self)

        # dev scenes
        self.dev_unit_data: UnitDataScene = UnitDataScene(self)
        self.dev_gallery: GalleryScene = GalleryScene(self)

        self.scene_stack: List[Scene] = []

        self.state: GameState = GameState.PLAYING

        self.master_clock = 0

        # activate main men
        self.add_scene(SceneType.MAIN_MENU)

        # record duration
        end_time = time.time()
        logging.info(f"Game initialised in {format(end_time - start_time, '.2f')}s.")

    def _update(self):
        # update delta time first
        self.window.update()
        delta_time = self.window.delta_time

        self.master_clock += delta_time

        self.input.update(delta_time)
        for scene in self.scene_stack:
            if scene.ui.is_active:
                scene.update(delta_time)
        self.debug.update(delta_time)

    def _render(self):
        # always refresh first
        self.window.refresh()

        surface = self.window.display
        for scene in self.scene_stack:
            if scene.ui.is_active:
                # handle those scenes that still have render methods
                # TODO - remove all render methods from Scene
                if scene in (self.combat, ):
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
        for scene in reversed(self.scene_stack):
            if scene.ui.is_active:
                scene.ui.process_input(delta_time)
                if scene.ui.block_onward_input:
                    break

        self.input.reset()

    def quit(self):
        self.state = GameState.EXITING

    def add_scene(self, scene_type: SceneType, activate: bool = True):
        """
        Add a scene to the scene stack
        """
        # reset input to ensure no input carries over between scenes
        self.input.reset()

        scene = self._scene_type_to_scene(scene_type)

        # add scene to active list
        self.scene_stack.append(scene)

        if activate:
            self.activate_scene(scene_type)

    def activate_scene(self, scene_type: SceneType):
        """
        Activate a scene. If specified scene isnt in the scene stack it is added.
        """
        scene = self._scene_type_to_scene(scene_type)

        if scene not in self.scene_stack:
            logging.warning(f"Scene activated [{scene_type}] was not in the scene_stack and so was added.")
            self.add_scene(scene_type)

        scene.activate()

    def remove_scene(self, scene_type: SceneType):
        """
        Remove a scene from the scene stack. Also deactivates
        """
        # reset input to ensure no input carries over between scenes
        self.input.reset()

        scene = self._scene_type_to_scene(scene_type)

        # clean up
        self.scene_stack.remove(scene)

    def deactivate_scene(self, scene_type: SceneType):
        """
        Deactivate a scene
        """
        scene = self._scene_type_to_scene(scene_type)

        if scene not in self.scene_stack:
            logging.warning(f"Scene to deactivate [{scene_type}] was not in the scene_stack and so was ignored.")
            return

        scene.deactivate()

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

    def change_scene(self, scene_types: List[SceneType]):
        """
        Deactivate all active scenes and activate the given scenes.
        """
        for scene in self.scene_stack:
            self.remove_scene(scene.type)

        for scene_type in scene_types:
            self.add_scene(scene_type)

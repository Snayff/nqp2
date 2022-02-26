from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import pygame as pygame

from scripts.core.assets import Assets
from scripts.core.base_classes.scene import Scene
from scripts.core.constants import GameState, SceneType
from scripts.core.data import Data
from scripts.core.debug import Debugger
from scripts.core.input import Input
from scripts.core.rng import RNG
from scripts.core.sounds import Sounds
from scripts.core.visuals import Visuals
from scripts.core.window import Window

if TYPE_CHECKING:
    from typing import List, Optional

__all__ = ["Game"]


############ TO DO LIST ############


class Game:
    def __init__(self):
        # imports here to avoid circular references since their core and
        # components require ``Game`` imports for typing.
        from scripts.core.memory import Memory
        from scripts.scenes.gallery.scene import GalleryScene
        from scripts.scenes.main_menu.scene import MainMenuScene
        from scripts.scenes.run_setup.scene import RunSetupScene
        from scripts.scenes.unit_data.scene import UnitDataScene
        from scripts.scenes.view_troupe.scene import ViewTroupeScene
        from scripts.scenes.world.scene import WorldScene

        # start timer
        start_time = time.time()

        # init libraries
        pygame.init()
        pygame.mixer.init()
        pygame.joystick.init()

        # managers
        self.debug: Debugger = Debugger(self)
        self.window: Window = Window(self)
        self.data: Data = Data(self)
        self.memory: Memory = Memory(self)
        self.assets: Assets = Assets(self)  # TODO - deprecate
        self.input: Input = Input(self)
        self.rng: RNG = RNG(self)
        self.sounds: Sounds = Sounds(self)
        self.visuals: Visuals = Visuals(self)

        # scenes
        # TODO - should these be private?
        self.main_menu: MainMenuScene = MainMenuScene(self)
        self.run_setup: RunSetupScene = RunSetupScene(self)
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
        self.master_clock += delta_time  # TODO - is this needed?

        # update input
        self.input.update(delta_time)
        # global handling of input to show debug info
        if self.input.states["tab"]:
            self.debug.toggle_debug_info()

        # update internal assets
        self.sounds.update(delta_time)
        self.visuals.update(delta_time)

        # update image ui
        for scene in self.scene_stack:
            if scene.ui.is_active:
                scene.update(delta_time)

        # update debug last
        self.debug.update(delta_time)

    def _draw(self):
        # always refresh first
        self.window.refresh()

        surface = self.window.display
        for scene in self.scene_stack:
            if scene.ui.is_active:
                scene.ui.draw(surface)

        self.debug.draw(surface)  # always last so it is on top

    def run(self):
        self._update()
        self._process_input()
        self._draw()

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
        for scene in self.scene_stack:
            scene.reset()
            self.remove_scene(scene.type)


        self.add_scene(scene_type)


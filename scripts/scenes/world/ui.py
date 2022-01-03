from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI
from scripts.core.constants import FontType, WorldState
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.terrain import Terrain
import pygame


from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union
    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene


__all__ = ["WorldUI"]


######### TO DO LIST ###############


class WorldUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        super().__init__(game, False)
        self.parent_scene: WorldScene = parent_scene

        # info pulled over from combat to render terrain
        self.camera: Camera = Camera()
        self.terrain: Terrain = Terrain(self.game)
        self.biome = "plains"
        self.mod_delta_time = 0  # actual delta time by combat speed
        self.combat_speed = 1
        self.force_idle = False


    def update(self, delta_time: float):
        super().update(delta_time)

        self.mod_delta_time = self.combat_speed * delta_time

        if not self.force_idle:
            self.terrain.update(self.mod_delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        self.camera.bind(self.terrain.boundaries)
        combat_surf = pygame.Surface(self.game.window.display.get_size())  # Not sure we need this?
        self.terrain.render(combat_surf, self.camera.render_offset())

        if self.parent_scene.state == WorldState.IDLE:
            self.parent_scene.units.render(combat_surf, self.camera.render_offset())

        # blit the terrain and units
        self.game.window.display.blit(
            combat_surf,
            (
                -(combat_surf.get_width() - self.game.window.display.get_width()) // 2,
                -(combat_surf.get_height() - self.game.window.display.get_height()) // 2,
            ),
        )

        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        self.terrain.generate(self.biome)


from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import FontType, WorldState
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.terrain import Terrain
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

        # TODO - info pulled over from combat to render terrain, needs clean up
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
        self.camera.bind(self.terrain.boundaries)
        combat_surf = pygame.Surface(self.game.window.display.get_size())  # Not sure we need this?
        self.terrain.render(combat_surf, self.camera.render_offset())

        if self.parent_scene.state == WorldState.IDLE:
            self.parent_scene.unit_manager.render(combat_surf, self.camera.render_offset())

        # blit the terrain and unit_manager
        self.game.window.display.blit(
            combat_surf,
            (
                -(combat_surf.get_width() - self.game.window.display.get_width()) // 2,
                -(combat_surf.get_height() - self.game.window.display.get_height()) // 2,
            ),
        )

        self.draw_grid(surface)
        self.draw_instruction(surface)
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        self.terrain.generate(self.biome)

    def draw_grid(self, surface: pygame.Surface):
        """
        Draw the unit selection grid
        """
        # TODO  - needs to be aligned to camera; move to camera?
        grid_size = self.parent_scene.grid_size
        grid_cell_size = self.parent_scene.grid_cell_size
        grid_margin = self.parent_scene.grid_margin
        line_colour = (0, 0, 0)

        # draw horizontal lines
        for h_line in range(grid_size[1] + 1):
            start_x = grid_margin
            start_y = h_line * grid_cell_size + grid_margin
            end_x = grid_size[0] * grid_cell_size + grid_margin
            end_y = h_line * grid_cell_size + grid_margin
            pygame.draw.line(surface, line_colour, (start_x, start_y), (end_x, end_y))

        # draw vertical lines
        for v_line in range(grid_size[0] + 1):
            start_x = v_line * grid_cell_size + grid_margin
            start_y = grid_margin
            end_x = v_line * grid_cell_size + grid_margin
            end_y = grid_size[1] * grid_cell_size + grid_margin
            pygame.draw.line(surface, line_colour, (start_x, start_y), (end_x, end_y))

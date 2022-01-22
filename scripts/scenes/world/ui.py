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
    from typing import Dict, List, Optional, Tuple, Type, Union

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
        self._parent_scene: WorldScene = parent_scene

        # TODO - info pulled over from combat to draw terrain, needs clean up
        self.camera: Camera = Camera()
        self.terrain: Terrain = Terrain(self._game)
        self.biome = "plains"
        self.mod_delta_time = 0  # actual delta time multiplied by game speed
        self.force_idle = False

    def update(self, delta_time: float):
        super().update(delta_time)

        self.mod_delta_time = self._game.memory.game_speed * delta_time

        if not self.force_idle:
            self.terrain.update(self.mod_delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # TODO  - replace when new room choice is in.
        if self._game.input.states["backspace"]:
            self._parent_scene.move_to_new_room()

    def draw(self, surface: pygame.surface):
        self.camera.bind(self.terrain.boundaries)
        combat_surf = pygame.Surface(self._game.window.display.get_size())  # Not sure we need this?
        self.terrain.draw(combat_surf, self.camera.render_offset())

        if self._parent_scene.state == WorldState.IDLE:
            self._draw_units(combat_surf, self.camera.render_offset())

        # blit the terrain and unit_manager
        self._game.window.display.blit(
            combat_surf,
            (
                -(combat_surf.get_width() - self._game.window.display.get_width()) // 2,
                -(combat_surf.get_height() - self._game.window.display.get_height()) // 2,
            ),
        )

        self._draw_grid(surface)
        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        self.terrain.generate(self.biome)

    def _draw_grid(self, surface: pygame.Surface):
        """
        Draw the unit selection grid
        """
        grid_size = self._parent_scene.grid_size
        grid_cell_size = self._parent_scene.grid_cell_size
        grid_margin = self._parent_scene.grid_margin
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

    def _draw_units(self, surface: pygame.surface, offset: Tuple[int, int] = (0, 0)):
        units = self._game.memory.player_troupe.units.values()

        for unit in units:
            unit.draw(surface, shift=offset)

        # organize entities for layered rendering
        entity_list = []
        for unit in units:
            for entity in unit.entities + unit.dead_entities:
                entity_list.append((entity.pos[1] + entity.img.get_height() // 2, len(entity_list), entity))

        entity_list.sort()

        for entity in entity_list:
            entity[2].draw(surface, shift=offset)

        for unit in units:
            unit.post_render(surface, shift=offset)

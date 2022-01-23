from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, SceneType, WorldState
from scripts.scene_elements.camera import Camera
from scripts.scene_elements.terrain import Terrain
from scripts.ui_elements.frame import Frame

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

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
        self.debug_pathfinding: bool = False

        self.victory_duration: float = 0

    def update(self, delta_time: float):
        super().update(delta_time)

        self.terrain.update(delta_time)

        self._update_camera_pos(delta_time)

        if self._parent_scene.state == WorldState.COMBAT_VICTORY:
            self.victory_duration += delta_time

            if self.victory_duration > 3:  # victory duration
                # remove enemy troupe
                self._game.memory.remove_troupe(self._parent_scene.enemy_troupe_id)

                # put units back to idle
                for troupe in self._game.memory.troupes.values():
                    troupe.set_force_idle(False)

                # reset info and reposition player's Troupe
                self._parent_scene.end_combat()
                self._parent_scene.align_unit_pos_to_unit_grid()

                # update state to prevent further updates
                self._parent_scene.state = WorldState.IDLE

                # refresh info shown
                self.rebuild_ui()

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # TODO  - replace when new room choice is in.
        if self._parent_scene.state == WorldState.IDLE:
            if self._game.input.states["backspace"]:
                self._parent_scene.move_to_new_room()
            if self._game.input.states["select"]:
                self._parent_scene.state = WorldState.COMBAT
                for troupe in self._game.memory.troupes.values():
                    troupe.set_force_idle(False)
        #############################################

        if self._parent_scene.state == WorldState.DEFEAT:
            if self._game.input.states["select"]:

                self._game.memory.reset()

                # return to main menu
                self._game.change_scene(SceneType.MAIN_MENU)

    def draw(self, surface: pygame.surface):
        self.camera.bind(self.terrain.boundaries)
        combat_surf = pygame.Surface(self._game.window.display.get_size())  # TODO Not sure we need this?

        self.terrain.draw(combat_surf, self.camera.render_offset())
        self._draw_units(combat_surf, self.camera.render_offset())

        if self.debug_pathfinding:
            self._draw_path_debug(surface)

        if self._parent_scene.state == WorldState.COMBAT:
            self._parent_scene.projectiles.draw(combat_surf, self.camera.render_offset())
            self._parent_scene.particles.draw(combat_surf, self.camera.render_offset())

        # handle camera zoom
        if self.camera.zoom != 1:
            combat_surf = pygame.transform.scale(
                combat_surf,
                (int(combat_surf.get_width() * self.camera.zoom), int(combat_surf.get_height() * self.camera.zoom)),
            )

        # blit the terrain and units
        self._game.window.display.blit(
            combat_surf,
            (
                -(combat_surf.get_width() - self._game.window.display.get_width()) // 2,
                -(combat_surf.get_height() - self._game.window.display.get_height()) // 2,
            ),
        )

        if self._parent_scene.state == WorldState.IDLE:
            self._draw_grid(surface)

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        self.terrain.generate(self.biome)

        create_font = self._game.assets.create_font

        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x = self._game.window.centre[0]
        start_y = self._game.window.centre[1]

        # draw upgrades
        current_x = start_x
        current_y = start_y

        if self._parent_scene.state == WorldState.DEFEAT:
            defeat_icon = self._game.assets.get_image("ui", "arrow_button", icon_size)
            frame = Frame(
                (current_x, current_y),
                image=defeat_icon,
                font=create_font(FontType.NEGATIVE, "Defeated"),
                is_selectable=False,
            )
            self._elements["defeat_notification"] = frame

            current_y += 100

            frame = Frame(
                (current_x, current_y),
                image=defeat_icon,
                font=create_font(FontType.DEFAULT, "Press Enter to return to the main menu."),
                is_selectable=False,
            )
            self._elements["defeat_instruction"] = frame

        if self._parent_scene.state == WorldState.COMBAT_VICTORY:
            frame = Frame(
                (current_x, current_y),
                font=create_font(FontType.POSITIVE, "Victory"),
                is_selectable=False,
            )
            self._elements["victory_notification"] = frame

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
        units = self._game.memory.get_all_units()

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

    def _draw_path_debug(self, surface: pygame.surface):
        """
        Draw lines to indicate the pathfinding
        """
        for entity in self._game.memory.get_all_entities():
            if entity._parent_unit.default_behaviour != "swarm":
                if entity.behaviour.current_path and len(entity.behaviour.current_path):
                    points = [
                        (p[0] + self.camera.render_offset()[0], p[1] + self.camera.render_offset()[1])
                        for p in ([entity.pos] + entity.behaviour.current_path)
                    ]
                    pygame.draw.lines(surface, (255, 0, 0), False, points)

    def _get_team_center(self, team) -> Optional[List]:
        count = 0
        pos_totals = [0, 0]
        for unit in self._game.memory.get_all_units():
            if unit.team == team:
                pos_totals[0] += unit.pos[0]
                pos_totals[1] += unit.pos[1]
                count += 1
        if count:
            return [pos_totals[0] / count, pos_totals[1] / count]
        else:
            return None

    def _update_camera_pos(self, delta_time):
        """
        Update the camera's position to follow the player's Units
        """
        target_pos = self._get_team_center("player")
        if not target_pos:
            target_pos = [0, 0]
        else:
            target_pos[0] -= self._game.window.base_resolution[0] // 2
            target_pos[1] -= self._game.window.base_resolution[1] // 2

        self.camera.pos[0] += (target_pos[0] - self.camera.pos[0]) / 10 * (delta_time * 60)
        self.camera.pos[1] += (target_pos[1] - self.camera.pos[1]) / 10 * (delta_time * 60)

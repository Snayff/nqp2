from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame

from scripts.world_elements.camera import Camera
from scripts.core import systems

if TYPE_CHECKING:
    from scripts.core.definitions import PointLike
    from scripts.core.game import Game
    from scripts.world_elements.world_model import WorldModel


__all__ = ["WorldView"]


class WorldView:
    """
    Render Terrain and game entities

    Attributes:
        camera: Used to show portions of the game world

    * Do not modify the state of the game, entities, terrain, etc.
    * Only draw the state of the game, nothing else

    The view should query the model or controller and make changes
    based on that info.  The view should not collect input from the
    user.

    """

    def __init__(self, game: Game, model: WorldModel):
        self._game = game
        self._model = model
        self._has_centered_camera: bool = False

        # interface
        self.camera = Camera(game.window.base_resolution)
        self.debug_pathfinding: bool = False
        self.clamp_primary_terrain: bool = True

    def update(self, delta_time: float):
        self._update_camera(delta_time)

    def draw(self, surface: pygame.Surface):
        if self.clamp_primary_terrain:
            self.camera.clamp(self._model.boundaries)
        else:
            next_boundaries = self._model.next_boundaries
            if next_boundaries.contains(self.camera.get_rect()):
                self.camera.clamp(next_boundaries)
            else:
                self.camera.clamp(self._model.total_boundaries)

        _surface = None
        if self.camera.zoom != 0.0:
            _surface = surface
            area = self.camera.get_rect()
            surface = pygame.Surface(area.size)

        offset = self.camera.render_offset()
        self._model.terrain.draw(surface, offset)
        if not self.clamp_primary_terrain:
            next_offset = offset + (self._model.terrain.boundaries.width, 0)
            self._model.next_terrain.draw(surface, next_offset)
        self._draw_units(surface, offset)
        self._model.projectiles.draw(surface, offset)
        self._model.particles.draw(surface, offset)

        if self.debug_pathfinding:
            self._draw_path_debug(surface)

        if _surface is not None:
            pygame.transform.scale(surface, _surface.get_size(), _surface)

    def reset_camera(self):
        self._has_centered_camera = False
        self._update_camera(0)

    def _update_camera(self, delta_time: float):
        """
        Update the camera's position to follow the player's Units
        """
        target_pos = self.get_team_center("player")
        if target_pos:
            self.camera.move_to_position(target_pos)
            self.camera.update(delta_time)
            # prevent camera from panning from 0,0
            if not self._has_centered_camera:
                self.camera.reset_movement()
                self._has_centered_camera = True

    def _draw_units(self, surface: pygame.Surface, offset: pygame.Vector2):
        units = self._model.get_all_units()

        systems.draw_entities(surface, shift=offset)


        # # organize entities for layered rendering
        # entity_list = []
        # for unit in units:
        #     for entity in unit.entities + unit.dead_entities:
        #         entity_list.append((entity.pos[1] + entity.img.get_height() // 2, len(entity_list), entity))
        #
        # entity_list.sort()
        #
        # for entity in entity_list:
        #     entity[2].draw(surface, shift=offset)

        for unit in units:
            if unit.team == "player":
                unit.draw_banner(surface, offset)

                if unit.is_selected:
                    unit.draw_border(surface, offset)


    def _draw_path_debug(self, surface: pygame.Surface):
        """
        Draw lines to indicate the pathfinding
        """
        for entity in self._model.get_all_entities():
            if entity._parent_unit.default_behaviour != "swarm":
                if entity.behaviour.current_path and len(entity.behaviour.current_path):
                    points = [
                        (p[0] + self.camera.render_offset()[0], p[1] + self.camera.render_offset()[1])
                        for p in ([entity.pos] + entity.behaviour.current_path)
                    ]
                    pygame.draw.lines(surface, (255, 0, 0), False, points)

    def get_team_center(self, team) -> Optional[pygame.Vector2]:
        """
        Get centre coordinates for the team
        """
        count = 0
        pos_totals = pygame.Vector2()
        for unit in self._model.get_all_units():
            if unit.team == team:
                pos_totals += unit.pos
                count += 1
        if count:
            return pygame.Vector2(pos_totals / count)
        else:
            return None

    def view_to_point(self, point: PointLike):
        """
        Return map pixel coords under the point

        * Point must be relative to the topleft corner of the view

        """
        offset = self.camera.render_offset()
        return pygame.Vector2(point) - offset

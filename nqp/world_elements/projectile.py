from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame
import snecs

from nqp.base_classes.image import Image
from nqp.core.components import Allegiance, DamageReceived, Position
from nqp.core.utility import angle_to

if TYPE_CHECKING:
    from typing import Dict, Tuple, Union

    from snecs.typedefs import EntityID

    from nqp.core.game import Game

__all__ = ["Projectile"]


class Projectile:
    def __init__(
        self, game: Game, owner: EntityID, target: EntityID, projectile_data: Dict[str, Union[Image, int]], damage: int
    ):
        self._game: Game = game
        self.owner: EntityID = owner
        self.target: EntityID = target
        self.image: Image = projectile_data["img"]
        self.speed: int = projectile_data["speed"]
        self.damage: int = damage

        position = snecs.entity_component(self.owner, Position)
        target_pos = snecs.entity_component(target, Position)
        self.angle: float = angle_to(position.pos, target_pos.pos)
        self.pos: pygame.Vector2 = (position.x, position.y - 5)  # move base firing position towards center of entity
        self.is_active: bool = True

    def update(self, delta_time: float):
        remaining_dis = self.speed * delta_time
        while remaining_dis > 0:
            dis = min(remaining_dis, 4)
            remaining_dis -= dis

            self.pos = ((self.pos[0] + math.cos(self.angle)) * dis, (self.pos[1] + math.sin(self.angle)) * dis)
            r = pygame.Rect(self.pos[0] - 4, self.pos[1] - 4, 8, 8)  # TODO - what are these magic numbers?

            # check out of bounds
            if not self._game.world.model.terrain.check_tile_hoverable(self.pos):
                self.is_active = False
                return

            for entity in self._game.world.model.get_all_entities():
                team = snecs.entity_component(self.owner, Allegiance).team
                other_team = snecs.entity_component(entity, Allegiance).team
                if team != other_team:
                    other_pos = snecs.entity_component(entity, Position)
                    if r.collidepoint(other_pos.pos):
                        snecs.add_component(entity, DamageReceived(self.damage))
                        self.is_active = False
                        return

    def draw(self, surf, offset: pygame.Vector2):
        rotated_img = pygame.transform.rotate(self.image.surface, -math.degrees(self.angle))
        surf.blit(
            rotated_img,
            (
                self.pos[0] - rotated_img.get_width() // 2 + offset[0],
                self.pos[1] - rotated_img.get_height() // 2 + offset[1],
            ),
        )

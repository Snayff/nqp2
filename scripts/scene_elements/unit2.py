from __future__ import annotations

import math
import random
from typing import Optional, TYPE_CHECKING

import pygame
import snecs

from scripts.core import queries
from scripts.core.components import IsDead, Position, Resources
from scripts.core.constants import StatModifiedStatus
from scripts.core.utility import itr
from scripts.scene_elements.entity import Entity

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from scripts.core.game import Game
    from snecs.typedefs import EntityID

__all__ = ["Unit2"]


class Unit2:
    def __init__(self, game: Game, id_: int, unit_type: str, team: str, pos: Tuple[int, int]):
        self._game: Game = game

        # get unit data
        unit_data = self._game.data.units[unit_type]
        base_values = self._game.data.config["unit_base_values"][f"tier_{unit_data['tier']}"]

        ######### Unit Info #############
        self.id = id_
        self.type: str = unit_type
        self.team: str = team  # this is derived from the Troupe but can be overridden in combat
        self.pos: Tuple[int, int] = pos
        self.is_selected: bool = False
        self.entities: List[EntityID] = []

        self.count: int = unit_data["count"] + base_values["count"]  # number of entities spawned
        self.gold_cost: int = unit_data["gold_cost"] + base_values["gold_cost"]
        self.entity_spread_max = unit_data["entity_spread"] if "entity_spread" in unit_data else 48
        self._banner_image = self._game.visual.get_image("banner")

        self.injuries: int = 0

        ######### Entity Info ##############
        # stats that dont use base values
        self.type: str = unit_data["type"]
        self.tier: int = unit_data["tier"]
        self.default_behaviour: str = unit_data["default_behaviour"]

        # stats that include base values
        self.health: int = unit_data["health"] + base_values["health"]
        self.attack: int = unit_data["attack"] + base_values["attack"]
        self.defence: int = unit_data["defence"] + base_values["defence"]
        self.range: int = unit_data["range"] + base_values["range"]
        self.attack_speed: float = unit_data["attack_speed"] + base_values["attack_speed"]
        self.move_speed: int = unit_data["move_speed"] + base_values["move_speed"]

        # ensure faux-null value is respected
        if unit_data["ammo"] in [-1, 0]:
            ammo_ = -1
        else:
            ammo_ = unit_data["ammo"] + base_values["ammo"]
        self._ammo: int = ammo_  # number of ranged shots

        self.uses_projectiles = self._ammo > 0
        self.size: int = unit_data["size"] + base_values["size"]  # size of the hitbox
        self.weight: int = unit_data["weight"] + base_values["weight"]
        self.projectile_data = (
            unit_data["projectile_data"] if "projectile_data" in unit_data else {"img": "arrow", "speed": 100}
        )

    def draw_banner(self, surface: pygame.Surface, shift: Tuple[int, int] = (0, 0)):
        """
        Draw's the Unit's banner.
        """
        banner_image = self._banner_image
        surface.blit(
            banner_image.surface,
            (
                self.pos[0] + shift[0] - banner_image.width // 2,
                self.pos[1] + shift[1] - 20 - banner_image.height,
            ),
        )

    def spawn_entities(self):
        """
        Spawn the Unit's Entities. Deletes any existing Entities first.
        """
        # prevent circular import error
        from scripts.core.components import Aesthetic, Knowledge, Position, Resources, Stats, Team, Projectiles

        self.delete_entities()

        for _ in range(self.count):
            # universal components
            components = [
                Position(self.pos),
                Aesthetic(self._game.visual.create_animation(self.type, "idle")),
                Resources(self.health),
                Stats(self),
                Team(self.team),
                Knowledge(),
            ]

            # conditional components
            if self.uses_projectiles:
                img = self._game.visual.get_image(self.projectile_data["img"])
                speed = self.projectile_data
                components.append(Projectiles(self._ammo, img, speed))

            # create entity
            self.entities.append(snecs.new_entity(components))

        self._align_entity_positions_to_unit()

    def delete_entities(self, immediately: bool = False):
        """
        Delete all entities. If "immediately" = False this will happen on the next frame.
        """
        if immediately:
            delete_func = snecs.delete_entity_immediately
        else:
            delete_func = snecs.schedule_for_deletion

        for entity in self.entities:
            delete_func(entity)

        self.entities = []

    def reset_for_combat(self):
        """
        Reset the in combat values ready to begin combat.
        """
        health = self.health
        for entity in self.entities:
            # heal to full
            resources = snecs.entity_component(entity, Resources)
            resources.health = health

            # remove dead flags
            if snecs.has_component(entity, IsDead):
                snecs.remove_component(entity, IsDead)

        self._align_entity_positions_to_unit()


    def update_position(self):
        """
        Update unit position by averaging the positions of all its entities.
        """
        num_entities = len(self.entities)
        if num_entities > 0:
            unit_pos = [0, 0]
            for entity in self.entities:
                entity_position = snecs.entity_component(entity, Position)
                unit_pos[0] += entity_position.x
                unit_pos[1] += entity_position.y
            self.pos = (unit_pos[0] / num_entities, unit_pos[1] / num_entities)

    def set_position(self, pos: Tuple[int, int]):
        """
        Set the unit's position and moves the Entities to match.
        """
        self.pos = pos
        self._align_entity_positions_to_unit()

    def _align_entity_positions_to_unit(self):
        unit_x = self.pos[0]
        unit_y = self.pos[1]
        max_spread = self.entity_spread_max

        for entity in self.entities:
            # randomise position in allowed area
            scatter_x = random.randint(- max_spread, max_spread)
            scatter_y = random.randint(- max_spread, max_spread)

            position = snecs.entity_component(entity, Position)
            position.pos = (unit_x + scatter_x, unit_y + scatter_y)



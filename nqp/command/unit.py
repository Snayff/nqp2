from __future__ import annotations

import random
from typing import Optional, TYPE_CHECKING

import pygame
import snecs

from nqp.core.constants import StatModifiedStatus

if TYPE_CHECKING:
    from typing import List, Tuple

    from snecs.typedefs import EntityID

    from nqp.core.game import Game

__all__ = ["Unit"]


class Unit:
    def __init__(self, game: Game, id_: int, unit_type: str, team: str, pos: pygame.Vector2):
        self._game: Game = game

        # get unit data
        unit_data = self._game.data.units[unit_type]
        base_values = self._game.data.config["unit_base_values"][f"tier_{unit_data['tier']}"]

        ######### Unit Info #############
        self.id = id_
        self.type: str = unit_type
        self.team: str = team  # this is derived from the Troupe but can be overridden in combat
        self.pos: pygame.Vector2 = pos
        self.is_selected: bool = False
        self.entities: List[EntityID] = []

        self.entity_spread_max = unit_data["entity_spread"] if "entity_spread" in unit_data else 48
        self.count: int = unit_data["count"] + base_values["count"]  # number of entities spawned
        self.gold_cost: int = unit_data["gold_cost" ""] + base_values["gold_cost"]
        self._banner_image = self._game.visual.get_image("banner")
        self.is_ranged: bool = True if unit_data["ammo"] > 0 else False
        self.default_behaviour: str = unit_data["default_behaviour"]  # load after other unit attrs
        # self.behaviour = self._game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        from nqp.command.unit_behaviour import UnitBehaviour  # prevent circular import

        self.behaviour: UnitBehaviour = UnitBehaviour(self._game, self)

        self.injuries: int = 0

        # border
        self.border_surface_timer: float = 0
        self.border_surface: Optional[pygame.surface] = None
        self.border_surface_offset: pygame.Vector2 = (0, 0)
        self.border_surface_outline: Optional[pygame.surface] = None
        self.border_surface_outline_black: Optional[pygame.surface] = None

        ######### Entity Info ##############
        # stats that dont use base values
        self.type: str = unit_data["type"]
        self.tier: int = unit_data["tier"]

        # stats that include base values
        self.health: int = unit_data["health"] + base_values["health"]
        self.attack: int = unit_data["attack"] + base_values["attack"]
        self.defence: int = unit_data["defence"] + base_values["defence"]
        self.range: int = unit_data["range"] + base_values["range"]
        self.attack_speed: float = unit_data["attack_speed"] + base_values["attack_speed"]
        self.move_speed: int = unit_data["move_speed"] + base_values["move_speed"]

        # ensure faux-null value is respected
        if unit_data["ammo"] in [-1, 0]:
            ammo = -1
        else:
            ammo = unit_data["ammo"] + base_values["ammo"]
        self._ammo: int = ammo  # number of ranged shots

        self.uses_projectiles = self._ammo > 0
        self.size: int = unit_data["size"] + base_values["size"]  # size of the hitbox
        self.weight: int = unit_data["weight"] + base_values["weight"]
        self.projectile_data = (
            unit_data["projectile_data"] if "projectile_data" in unit_data else {"img": "arrow", "speed": 100}
        )

    def update(self, delta_time: float):
        # refresh the border
        if self.team == "player":
            self.border_surface_timer += delta_time
            if self.border_surface_timer > 0.5:
                self.border_surface_timer -= 0.5
                self.generate_border_surface()

        self.behaviour.update(delta_time)
        self.update_position()

    @property
    def is_alive(self):
        from nqp.core.components import IsDead  # prevent circular import

        for entity in self.entities:
            if not snecs.has_component(entity, IsDead):
                return True
        return False

    def draw_banner(self, surface: pygame.Surface, shift: pygame.Vector2 = (0, 0)):
        """
        Draw's the Unit's banner.
        """
        banner_image = self._banner_image
        surface.blit(
            banner_image.surface,
            (
                self.pos.x + shift[0] - banner_image.width // 2,
                self.pos.y + shift[1] - 20 - banner_image.height,
            ),
        )

    def draw_border(self, surface: pygame.Surface, shift: pygame.Vector2 = (0, 0)):
        """
        Draw the border around the unit.
        """
        for d in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            surface.blit(
                self.border_surface_outline_black,
                (
                    self.pos.x + shift[0] - self.border_surface_offset[0] + d[0],
                    self.pos.y + shift[1] - self.border_surface_offset[1] + d[1],
                ),
            )
        surface.blit(
            self.border_surface,
            (
                self.pos.x + shift[0] - self.border_surface_offset[0],
                self.pos.y + shift[1] - self.border_surface_offset[1],
            ),
        )
        surface.blit(
            self.border_surface_outline,
            (
                self.pos.x + shift[0] - self.border_surface_offset[0],
                self.pos.y + shift[1] - self.border_surface_offset[1],
            ),
        )

    def spawn_entities(self):
        """
        Spawn the Unit's Entities. Deletes any existing Entities first.
        """
        # prevent circular import error
        from nqp.core.components import Aesthetic, AI, Allegiance, Position, RangedAttack, Resources, Stats

        self.delete_entities()

        for _ in range(self.count):
            # universal components
            components = [
                Position(self.pos),  # TODO - fix being passed tuple
                Aesthetic(self._game.visual.create_animation(self.type, "idle")),
                Resources(self.health),
                Stats(self),
                Allegiance(self.team, self),
            ]

            # conditional components
            if self.uses_projectiles:
                img = self._game.visual.get_image(self.projectile_data["img"])
                speed = self.projectile_data
                components.append(RangedAttack(self._ammo, img, speed))

            # create entity
            entity = snecs.new_entity(components)
            self.entities.append(entity)

            # add components that need ref to entity
            from nqp.command.basic_entity_behaviour import BasicEntityBehaviour  # prevent circular import

            snecs.add_component(entity, AI(BasicEntityBehaviour(self._game, self, entity)))

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
        # prevent circular import
        from nqp.core.components import DamageReceived, IsDead, IsReadyToAttack, RangedAttack, Resources

        health = self.health
        for entity in self.entities:
            # heal to full
            resources = snecs.entity_component(entity, Resources)
            resources.health = health

            # remove flags
            if snecs.has_component(entity, IsDead):
                snecs.remove_component(entity, IsDead)
            if snecs.has_component(entity, IsReadyToAttack):
                snecs.remove_component(entity, IsReadyToAttack)
            if snecs.has_component(entity, DamageReceived):
                snecs.remove_component(entity, DamageReceived)

            # reset ammo
            if snecs.has_component(entity, RangedAttack):
                ranged = snecs.entity_component(entity, RangedAttack)
                ranged.ammo.reset()

        self._align_entity_positions_to_unit()

    def update_position(self):
        """
        Update unit position by averaging the positions of all its entities.
        """
        from nqp.core.components import Position  # prevent circular import

        num_entities = len(self.entities)
        if num_entities > 0:
            unit_pos = [0, 0]
            for entity in self.entities:
                entity_position = snecs.entity_component(entity, Position)
                unit_pos[0] += entity_position.x
                unit_pos[1] += entity_position.y
            self.pos = (unit_pos[0] / num_entities, unit_pos[1] / num_entities)

    def set_position(self, pos: pygame.Vector2):
        """
        Set the unit's position and moves the Entities to match.
        """
        self.pos = pos
        self._align_entity_positions_to_unit()

    def _align_entity_positions_to_unit(self):
        from nqp.core.components import Position  # prevent circular import

        unit_x = self.pos.x
        unit_y = self.pos.y
        max_spread = self.entity_spread_max

        for entity in self.entities:
            # randomise position in allowed area
            scatter_x = random.randint(-max_spread, max_spread)
            scatter_y = random.randint(-max_spread, max_spread)

            position = snecs.entity_component(entity, Position)
            position.pos = (unit_x + scatter_x, unit_y + scatter_y)

    def generate_border_surface(self):
        """
        Generate a new border around the Unit. Stub
        """
        if len(self.entities):
            # FIXME - throws "ValueError: points argument must contain 2 or more points" and draws incorrectly
            pass
            # surf_padding = 20
            # outline_padding = 10
            # self.border_surface = None
            #
            # # get entity positions
            # from scripts.core.components import Position  # prevent circular import
            #
            # all_positions = []
            # for entity in self.entities:
            #     position = snecs.entity_component(entity, Position)
            #     all_positions.append(position.pos)
            #
            # all_x = [p[0] for p in all_positions]
            # all_y = [p[1] for p in all_positions]
            # min_x = min(all_x)
            # min_y = min(all_y)
            # self.border_surface = pygame.Surface(
            #     (max(all_x) - min_x + surf_padding * 2, max(all_y) - min_y + surf_padding * 2)
            # )
            # self.border_surface_offset = (self.pos.x - min_x + surf_padding, self.pos.y - min_y + surf_padding)
            # self.border_surface.set_colorkey((0, 0, 0))
            #
            # points = [
            #     (self.pos.x - outline_padding, self.pos.y),
            #     (self.pos.x, self.pos.y - outline_padding),
            #     (self.pos.x + outline_padding, self.pos.y),
            #     (self.pos.x, self.pos.y + outline_padding),
            # ]
            #
            # placed_points = []
            #
            # for pos in all_positions + points:
            #     new_pos = (pos[0] - min_x + surf_padding, pos[1] - min_y + surf_padding)
            #     angle = math.atan2(pos[1] - self.pos.y, pos[0] - self.pos.x)
            #     new_pos = (
            #         new_pos[0] + outline_padding * math.cos(angle),
            #         new_pos[1] + outline_padding * math.sin(angle),
            #     )
            #     for p in placed_points:
            #         pygame.draw.line(self.border_surface, (255, 255, 255), new_pos, p)
            #     placed_points.append(new_pos)
            #
            # mask_surf = pygame.mask.from_surface(self.border_surface)
            #
            # self.border_surface.fill((0, 0, 0))
            # self.border_surface_outline = self.border_surface.copy()
            # self.border_surface_outline_black = self.border_surface.copy()
            #
            # outline = mask_surf.outline(2)
            # pygame.draw.lines(self.border_surface_outline, (255, 255, 255), False, outline)
            # pygame.draw.lines(self.border_surface_outline_black, (0, 0, 1), False, outline)
            # pygame.draw.polygon(self.border_surface, (0, 0, 255), outline)
            # self.border_surface.set_alpha(80)

    def add_modifier(self, stat: str, amount: int):
        """
        Add a modifier to a stat. Stub
        """
        # FIXME - stubbed
        pass

    def get_modified_status(self, stat: str) -> StatModifiedStatus:
        """
        Check if a given stat is modified. Stub.
        """
        # FIXME - stubbed
        pass

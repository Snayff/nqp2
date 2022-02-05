from __future__ import annotations

import math
import random
from typing import Optional, TYPE_CHECKING

import pygame

from scripts.core.constants import StatModifiedStatus
from scripts.core.utility import itr
from scripts.scene_elements.entity import Entity

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from scripts.core.game import Game

__all__ = ["Unit"]


class Unit:
    def __init__(self, game: Game, id_: int, unit_type: str, team: str):
        self._game: Game = game

        # persistent
        unit_data = self._game.data.units[unit_type]
        self.id = id_
        self.type: str = unit_type
        self.team: str = team  # this is derived from the Troupe but can be overridden in combat

        # stats that dont use base values
        self.type: str = unit_data["type"]
        self.tier: int = unit_data["tier"]
        self.default_behaviour: str = unit_data["default_behaviour"]

        # stats that include
        base_values = self._game.data.config["unit_base_values"][f"tier_{unit_data['tier']}"]
        self._health: int = unit_data["health"] + base_values["health"]
        self._attack: int = unit_data["attack"] + base_values["attack"]
        self._defence: int = unit_data["defence"] + base_values["defence"]
        self._range: int = unit_data["range"] + base_values["range"]
        self._attack_speed: float = unit_data["attack_speed"] + base_values["attack_speed"]
        self._move_speed: int = unit_data["move_speed"] + base_values["move_speed"]

        # ensure faux-null value is respected
        if unit_data["ammo"] in [-1, 0]:
            ammo_ = -1
        else:
            ammo_ = unit_data["ammo"] + base_values["ammo"]
        self._ammo: int = ammo_  # number of ranged shots

        self.use_ammo = self._ammo > 0
        self.count: int = unit_data["count"] + base_values["count"]  # number of entities spawned
        self.size: int = unit_data["size"] + base_values["size"]  # size of the hitbox
        self.weight: int = unit_data["weight"] + base_values["weight"]
        self.gold_cost: int = unit_data["gold_cost"] + base_values["gold_cost"]
        self.projectile_data = (
            unit_data["projectile_data"] if "projectile_data" in unit_data else {"img": "arrow", "speed": 100}
        )
        self.entity_spread_max = unit_data["entity_spread"] if "entity_spread" in unit_data else 48

        self.modifiers: Dict[str, List[int]] = {}

        self.injuries: int = 0

        # stats recording
        self.damage_dealt: int = 0
        self.damage_received: int = 0
        self.kills: int = 0

        self.behaviour = self._game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        self.alive: bool = True
        self.colour = (0, 0, 255)
        self.entities: List[Entity] = []
        self.dead_entities: List[Entity] = []
        self.pos: List[int, int] = [0, 0]
        self.placed: bool = False
        self.forced_idle: bool = True  # forces idle state to prevent action

        # visual
        self.border_surface_timer: float = 0
        self.border_surface: Optional[pygame.surface] = None
        self.border_surface_offset: Tuple[int, int] = (0, 0)
        self.border_surface_outline: Optional[pygame.surface] = None
        self.border_surface_outline_black: Optional[pygame.surface] = None

    @property
    def health(self) -> int:
        value = self._health

        try:
            for mod in self.modifiers["health"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def attack(self) -> int:
        value = self._attack

        try:
            for mod in self.modifiers["attack"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def defence(self) -> int:
        value = self._defence

        try:
            for mod in self.modifiers["defence"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def attack_speed(self) -> float:
        value = self._attack_speed

        try:
            for mod in self.modifiers["attack_speed"]:
                value += mod

        except KeyError:
            pass

        return value

    @property
    def range(self) -> int:
        value = self._range

        try:
            for mod in self.modifiers["range"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def move_speed(self) -> int:
        value = self._move_speed

        try:
            for mod in self.modifiers["move_speed"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def ammo(self) -> int:
        value = self._ammo

        try:
            for mod in self.modifiers["ammo"]:
                value += mod

        except KeyError:
            pass

        return value

    def gen_border_surface(self):
        if len(self.entities):
            surf_padding = 20
            outline_padding = 10
            self.border_surface = None
            all_positions = [entity.pos for entity in self.entities]
            all_x = [p[0] for p in all_positions]
            all_y = [p[1] for p in all_positions]
            min_x = min(all_x)
            min_y = min(all_y)
            self.border_surface = pygame.Surface(
                (max(all_x) - min_x + surf_padding * 2, max(all_y) - min_y + surf_padding * 2)
            )
            self.border_surface_offset = (self.pos[0] - min_x + surf_padding, self.pos[1] - min_y + surf_padding)
            self.border_surface.set_colorkey((0, 0, 0))

            points = [
                (self.pos[0] - outline_padding, self.pos[1]),
                (self.pos[0], self.pos[1] - outline_padding),
                (self.pos[0] + outline_padding, self.pos[1]),
                (self.pos[0], self.pos[1] + outline_padding),
            ]

            placed_points = []

            for pos in all_positions + points:
                new_pos = (pos[0] - min_x + surf_padding, pos[1] - min_y + surf_padding)
                angle = math.atan2(pos[1] - self.pos[1], pos[0] - self.pos[0])
                new_pos = (
                    new_pos[0] + outline_padding * math.cos(angle),
                    new_pos[1] + outline_padding * math.sin(angle),
                )
                for p in placed_points:
                    pygame.draw.line(self.border_surface, (255, 255, 255), new_pos, p)
                placed_points.append(new_pos)

            mask_surf = pygame.mask.from_surface(self.border_surface)

            self.border_surface.fill((0, 0, 0))
            self.border_surface_outline = self.border_surface.copy()
            self.border_surface_outline_black = self.border_surface.copy()

            outline = mask_surf.outline(2)
            pygame.draw.lines(self.border_surface_outline, (255, 255, 255), False, outline)
            pygame.draw.lines(self.border_surface_outline_black, (0, 0, 1), False, outline)
            pygame.draw.polygon(self.border_surface, (0, 0, 255), outline)
            self.border_surface.set_alpha(80)

    def update(self, dt):
        self.update_pos()

        if self.team == "player":
            self.border_surface_timer += dt
            if self.border_surface_timer > 0.5:
                self.border_surface_timer -= 0.5
                self.gen_border_surface()

        # a unit is alive if all of its entities are alive
        self.alive = bool(len(self.entities))

        if self.forced_idle == False:
            self.behaviour.process(dt)

        for i, entity in enumerate(self.dead_entities):
            entity.update(dt)

        for i, entity in itr(self.entities):
            entity.update(dt)

            # remove if dead
            if not entity.alive:
                self.entities.pop(i)
                self.dead_entities.append(entity)

    def draw(self, surface: pygame.Surface, shift=(0, 0)):
        if self.team == "player":
            for d in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                surface.blit(
                    self.border_surface_outline_black,
                    (
                        self.pos[0] + shift[0] - self.border_surface_offset[0] + d[0],
                        self.pos[1] + shift[1] - self.border_surface_offset[1] + d[1],
                    ),
                )
            surface.blit(
                self.border_surface,
                (
                    self.pos[0] + shift[0] - self.border_surface_offset[0],
                    self.pos[1] + shift[1] - self.border_surface_offset[1],
                ),
            )
            surface.blit(
                self.border_surface_outline,
                (
                    self.pos[0] + shift[0] - self.border_surface_offset[0],
                    self.pos[1] + shift[1] - self.border_surface_offset[1],
                ),
            )

    def post_render(self, surface: pygame.Surface, shift=(0, 0)):
        if self.team == "player":
            # TODO - should be swapped when banner assets are added
            banner_img = self._game.assets.ui["banner"]
            surface.blit(
                banner_img,
                (
                    self.pos[0] + shift[0] - banner_img.get_width() // 2,
                    self.pos[1] + shift[1] - 20 - banner_img.get_height(),
                ),
            )

    def reset_for_combat(self):
        """
        Reset the in combat values ready to begin combat.
        """
        self.behaviour = self._game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        self.alive = True
        self.placed = False

        self.damage_dealt = 0
        self.damage_received = 0
        self.kills = 0

        if self.team == "player":
            self.colour = (0, 0, 255)
        else:
            self.colour = (255, 0, 0)

        self.entities = []
        self.dead_entities = []

    def spawn_entities(self):
        """
        Spawn the unit's entities.
        """
        for i in range(self.count):
            self.entities.append(Entity(self))

        self.update_pos()

        # stuff for the border surface (updates every 0.5s)
        if self.team == "player":
            self.border_surface_timer = random.random() * 0.5
            self.gen_border_surface()

    def update_pos(self):
        """
        Update unit "position" by averaging the positions of all its entities.
        """
        if len(self.entities):
            pos = [0, 0]
            for entity in self.entities:
                pos[0] += entity.pos[0]
                pos[1] += entity.pos[1]
            self.pos[0] = pos[0] / len(self.entities)
            self.pos[1] = pos[1] / len(self.entities)

    def set_position(self, pos: List[int, int]):
        """
        Set the unit's position.
        """
        self.entities = []

        self.pos = pos
        self.spawn_entities()

    def add_modifier(self, stat: str, amount: int):
        """
        Add a modifier to a stat.
        """
        if stat in self.modifiers:
            self.modifiers[stat].append(amount)

        else:
            self.modifiers[stat] = [amount]

    def get_modified_status(self, stat: str) -> StatModifiedStatus:
        """
        Check if a given stat is modified.
        """
        modifiers = self.modifiers

        if stat in modifiers:
            has_negatives = any(n < 0 for n in modifiers[stat])
            has_positives = any(n > 0 for n in modifiers[stat])

            if has_negatives and has_positives:
                status = StatModifiedStatus.POSITIVE_AND_NEGATIVE
            elif has_negatives and not has_positives:
                status = StatModifiedStatus.NEGATIVE
            else:
                # not has_negatives and has_positives
                status = StatModifiedStatus.POSITIVE
        else:
            status = StatModifiedStatus.NONE

        return status

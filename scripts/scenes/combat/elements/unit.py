from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.utility import itr
from scripts.scenes.combat.elements.entity import Entity

if TYPE_CHECKING:
    from typing import List

    from scripts.core.game import Game

__all__ = ["Unit"]


class Unit:
    def __init__(self, game: Game, id_: int, unit_type: str, team: str, is_upgraded: bool = False):
        self.game: Game = game

        # persistent
        unit_data = self.game.data.units[unit_type]
        self.id = id_
        self.type: str = unit_type
        self.is_upgraded = is_upgraded
        self.team: str = team

        # determine which value to get from tuple
        if is_upgraded:
            i = 1
        else:
            i = 0

        self.health: int = unit_data["health"][i]
        self.attack: int = unit_data["attack"][i]
        self.defence: int = unit_data["defence"][i]
        self.range: int = unit_data["range"][i]
        self.attack_speed: float = unit_data["attack_speed"][i]
        self.move_speed: int = unit_data["move_speed"][i]
        self.ammo: int = unit_data["ammo"][i]
        self.count: int = unit_data["count"][i]
        self.size: int = unit_data["size"][i]
        self.weight: int = unit_data["weight"][i]
        self.gold_cost: int = unit_data["gold_cost"][i]

        self.default_behaviour: str = unit_data["default_behaviour"]
        self.upgrade_cost: int = unit_data["upgrade_cost"]

        # in combat
        self.behaviour = self.game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        self.alive: bool = True
        self.colour = (0, 0, 255)
        self.entities: List[Entity] = []
        self.pos: List[int, int] = [0, 0]
        self.placed: bool = False

    def reset_for_combat(self):
        """
        Reset the in combat values ready to begin combat.
        """
        self.behaviour = self.game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        self.alive = True
        self.placed = False

        if self.team == "player":
            self.colour = (0, 0, 255)
        else:
            self.colour = (255, 0, 0)

        self.entities = []

    def spawn_entities(self):
        """
        Spawn the unit's entities.
        """
        for i in range(self.count):
            self.entities.append(Entity(self))

    def update_pos(self):
        """
        Update unit "position" by averaging the positions of all its entities.
        """
        if not self.entities:
            pos = [0, 0]
            for entity in self.entities:
                pos[0] += entity.pos[0]
                pos[1] += entity.pos[1]
            self.pos[0] = pos[0] / len(self.entities)
            self.pos[1] = pos[1] / len(self.entities)

    def upgrade(self):
        """
        Upgrade the unit and their stats
        """
        self.is_upgraded = True

        # update stats
        unit_data = self.game.data.units[self.type]
        i = 1
        self.health: int = unit_data["health"][i]
        self.attack: int = unit_data["attack"][i]
        self.defence: int = unit_data["defence"][i]
        self.range: int = unit_data["range"][i]
        self.attack_speed: float = unit_data["attack_speed"][i]
        self.move_speed: int = unit_data["move_speed"][i]
        self.ammo: int = unit_data["ammo"][i]
        self.count: int = unit_data["count"][i]
        self.size: int = unit_data["size"][i]
        self.weight: int = unit_data["weight"][i]
        self.gold_cost: int = unit_data["gold_cost"][i]

    def update(self, dt):
        self.update_pos()

        # a unit is alive if all of its entities are alive
        self.alive = bool(len(self.entities))

        self.behaviour.process(dt)

        for i, entity in itr(self.entities):
            entity.update(dt)

            # remove if dead
            if not entity.alive:
                self.entities.pop(i)

    def render(self, surface: pygame.Surface, shift=(0, 0)):
        for entity in self.entities:
            entity.render(surface, shift=shift)

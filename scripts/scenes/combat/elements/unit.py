from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.game import Game
from scripts.core.utility import itr
from scripts.scenes.combat.elements.entity import Entity

if TYPE_CHECKING:
    from typing import List

__all__ = ["Unit"]


class Unit:
    def __init__(self, game: Game, id_: int, unit_type: str, team: str):
        self.game: Game = game

        # persistent
        unit_data = self.game.data.units[unit_type]
        self.id = id_
        self.type: str = unit_type
        self.health: int = unit_data["health"]
        self.defense: int = unit_data["defense"]
        self.damage: int = unit_data["damage"]
        self.range: int = unit_data["range"]
        self.attack_speed: int = unit_data["attack_speed"]
        self.move_speed: int = unit_data["move_speed"]
        self.ammo: int = unit_data["ammo"]
        self.count: int = unit_data["count"]
        self.size: int = unit_data["size"]
        self.weight: int = unit_data["weight"]
        self.default_behavior: str = unit_data["default_behaviour"]
        self.gold_cost: int = unit_data["gold_cost"]
        self.team: str = team

        # in combat
        self.behavior = self.game.data.behaviors.unit_behaviors[self.default_behavior](self)
        self.alive: bool = True
        self.colour = (0, 0, 255)
        self.entities: List[Entity] = []
        self.pos: List[int, int] = [0, 0]

    def reset_for_combat(self):
        """
        Reset the in combat values ready to begin combat.
        """
        self.behavior = self.game.data.behaviors.unit_behaviors[self.default_behavior](self)
        self.alive = True

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

    def update(self, dt):
        self.update_pos()

        # a unit is alive if all of its entities are alive
        self.alive = bool(len(self.entities))

        self.behavior.process(dt)

        for i, entity in itr(self.entities):
            entity.update(dt)

            # remove if dead
            if not entity.alive:
                self.entities.pop(i)

    def render(self, surface: pygame.Surface, shift=(0, 0)):
        for entity in self.entities:
            entity.render(surface, shift=shift)

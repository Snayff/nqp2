from typing import List

import pygame

from scripts.core.utility import itr
from scripts.scenes.combat.elements.entity import Entity


class Unit:
    def __init__(self, game, unit_type, pos: List = None, team="player"):
        # handle mutable arg
        if pos is None:
            pos = [0, 0]

        self.game = game
        self.type = unit_type
        self.stats = self.game.memory.units[self.type].copy()
        self.pos = list(pos)
        self.team = team

        self.behavior_type = self.stats["default_behavior"]
        self.behavior = self.game.memory.behaviors.unit_behaviors[self.behavior_type](self)

        self.alive = True

        # temporary
        if self.team == "player":
            self.color = (0, 0, 255)
        else:
            self.color = (255, 0, 0)

        self.entities = []

    def update_pos(self):
        """
        Update unit "position" by averaging the positions of all its entities.
        """

        if self.entities != []:
            pos = [0, 0]
            for entity in self.entities:
                pos[0] += entity.pos[0]
                pos[1] += entity.pos[1]
            self.pos[0] = pos[0] / len(self.entities)
            self.pos[1] = pos[1] / len(self.entities)

    def spawn_entities(self):
        for i in range(self.stats["count"]):
            self.entities.append(Entity(self))

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

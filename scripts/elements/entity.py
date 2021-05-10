import math
import random

import pygame

from scripts.misc.utility import offset
from scripts.misc.constants import WEIGHT_SCALE, PUSH_FORCE, DEFENSE_SCALE

'''
Don't try to enforce typing with some of the functions here. They're meant to take anything with a "pos" attribute.
This can be adjusted to have valid typing, but it'd make a lot of stuff unnecessarily complicated.
'''

class Entity:
    def __init__(self, parent_unit):
        self.unit = parent_unit
        self.game = self.unit.game
        self.pos = self.unit.pos.copy()
        self.team = self.unit.team
        self.stats = self.unit.stats.copy()

        self.behavior = self.game.memory.behaviors.entity_behaviors[self.unit.behavior_type](self)

        self.attack_timer = 0
        self.pushed_by_log = []
        self.pushed_log = []
        self.damaged_by_log = []

        self.alive = True

        # slightly adjust position so the initial spread is round
        self.pos[0] += random.random() * 0.1 - 0.05
        self.pos[1] += random.random() * 0.1 - 0.05

        # temp
        self.color = self.unit.color

    def dis(self, entity):
        '''
        Find the distance to another entity or other object with a position.
        '''
        return math.sqrt((self.pos[0] - entity.pos[0]) ** 2 + (self.pos[1] - entity.pos[1]) ** 2)

    def angle(self, entity):
        '''
        Find the angle to another entity or other object with a position.
        '''
        return math.atan2(entity.pos[1] - self.pos[1], entity.pos[0] - self.pos[0])

    def advance(self, angle, amount):
        self.pos[0] += math.cos(angle) * amount
        self.pos[1] += math.sin(angle) * amount

    def damage(self, amount, owner):
        self.stats['health'] -= amount * (DEFENSE_SCALE / (DEFENSE_SCALE + self.stats['defense']))
        if self.stats['health'] <= 0:
            self.stats['health'] = 0
            self.alive = False

        self.damaged_by_log = (self.damaged_by_log + [owner])[-30:]

    def attempt_attack(self, entity):
        if self.attack_timer <= 0:
            self.attack_timer = 1 / self.stats['attack_speed']
            if self.dis(entity) - (entity.stats['size'] + self.stats['size']) < self.stats['range']:
                entity.damage(self.stats['damage'], self)
                self.attack_timer = 1 / self.stats['attack_speed']

    def update(self, dt):
        self.attack_timer = max(0, self.attack_timer - dt)

        self.behavior.process(dt)

        # handle collision
        for entity in self.game.combat.all_entities:
            if entity != self:
                combined_size = self.stats['size'] + entity.stats['size']
                # horizontal scan
                if abs(entity.pos[0] - self.pos[0]) < combined_size:
                    # vertical scan
                    if abs(entity.pos[1] - self.pos[1]) < combined_size:
                        # full check instead of rough
                        dis = self.dis(entity)
                        if dis < combined_size:
                            # push both (pushing gets doubled)
                            angle = self.angle(entity)
                            force = (1 - dis / combined_size)
                            entity.advance(angle, (self.stats['weight'] + WEIGHT_SCALE) / (entity.stats['weight'] + WEIGHT_SCALE) * dt * PUSH_FORCE * force)
                            self.advance(angle + math.pi, (entity.stats['weight'] + WEIGHT_SCALE) / (self.stats['weight'] + WEIGHT_SCALE) * dt * PUSH_FORCE * force)
                            entity.pushed_by_log = (entity.pushed_by_log + [self])[-30:]
                            self.pushed_log = (self.pushed_log + [entity])[-30:]


    def render(self, surface: pygame.Surface, shift=(0, 0)):
        pygame.draw.circle(surface, self.color, offset(shift.copy(), self.pos), self.stats['size'])

        # debug stuff for swarm targeting
        if self.behavior.priority_target:
            pygame.draw.line(surface, (255, 0, 255), offset(shift.copy(), self.pos), offset(shift.copy(), self.behavior.priority_target.pos))
        elif self.unit.behavior.target:
            pygame.draw.line(surface, (255, 255, 0), offset(shift.copy(), self.pos), offset(shift.copy(), self.unit.behavior.target.pos))

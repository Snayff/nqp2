import math
import random

from scripts.scenes.combat.elements.entity_behaviours.behaviour import Behaviour


class Swarm(Behaviour):
    def complete_init(self):
        self.priority_target = None
        self.loop_around = 0
        self.loop_direction = random.choice([random.random() * 2 - 1, 0])  # don't use seeded rng

    def process(self, dt):
        # reduce loop around timer
        self.loop_around = max(-0.5, self.loop_around - dt)

        self.entity.action = 'walk'

        # set priority target if bumped
        if self.entity.pushed_log != []:
            for entity in self.entity.pushed_log[::-1]:
                if entity.team != self.entity.team:
                    self.priority_target = entity
                elif self.loop_around <= -0.5:
                    self.loop_around = 0.5
            self.entity.pushed_log = []

        if self.entity.pushed_by_log != []:
            for entity in self.entity.pushed_by_log[::-1]:
                if entity.team != self.entity.team:
                    self.priority_target = entity
                elif self.loop_around <= -0.5:
                    self.loop_around = 0.5
            self.entity.pushed_by_log = []

        # turn on attacker
        if self.entity.damaged_by_log != []:
            for entity in self.entity.pushed_by_log[::-1]:
                if entity.range < self.entity.range * 1.2:
                    self.priority_target = entity
            self.entity.damaged_by_log = []

        if self.priority_target:
            dis = self.entity.dis(self.priority_target) - (self.entity.size + self.priority_target.size)
            if dis > self.entity.range:
                angle = self.entity.angle(self.priority_target)
                self.entity.advance(angle, self.entity.move_speed * dt)

            # always try to attack
            self.entity.action = 'attack'
            self.entity.attempt_attack(self.priority_target)

            # add a case to cancel if the target gets away
            if dis > self.entity.range * 2:
                self.priority_target = None

            # check if target is dead
            elif not self.priority_target.alive:
                self.priority_target = None

        elif self.entity.unit.behaviour.target:
            angle = self.entity.angle(self.entity.unit.behaviour.target)

            if self.loop_around > 0:
                self.entity.advance(angle + (math.pi / 1.7) * self.loop_direction, self.entity.move_speed * dt)

            else:
                dis = self.entity.dis(self.entity.unit.behaviour.target) - (
                    self.entity.size + self.entity.unit.behaviour.target.size
                )
                if dis > self.entity.range:
                    self.entity.advance(angle, self.entity.move_speed * dt)

                # always try to attack
                self.entity.action = 'attack'
                self.entity.attempt_attack(self.entity.unit.behaviour.target)

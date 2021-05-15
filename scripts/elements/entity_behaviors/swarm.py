import math
import random

from scripts.elements.entity_behaviors.behavior import Behavior


class Swarm(Behavior):
    def complete_init(self):
        self.priority_target = None
        self.loop_around = 0
        self.loop_direction = random.choice([random.random() * 2 - 1, 0])

    def process(self, dt):
        # reduce loop around timer
        self.loop_around = max(-0.5, self.loop_around - dt)

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
                if entity.stats["range"] < self.entity.stats["range"] * 1.2:
                    self.priority_target = entity
            self.entity.damaged_by_log = []

        if self.priority_target:
            dis = self.entity.dis(self.priority_target) - (
                self.entity.stats["size"] + self.priority_target.stats["size"]
            )
            if dis > self.entity.stats["range"]:
                angle = self.entity.angle(self.priority_target)
                self.entity.advance(angle, self.entity.stats["move_speed"] * dt)

            # always try to attack
            self.entity.attempt_attack(self.priority_target)

            # add a case to cancel if the target gets away
            if dis > self.entity.stats["range"] * 2:
                self.priority_target = None

            # check if target is dead
            elif not self.priority_target.alive:
                self.priority_target = None

        elif self.entity.unit.behavior.target:
            angle = self.entity.angle(self.entity.unit.behavior.target)

            if self.loop_around > 0:
                self.entity.advance(angle + (math.pi / 1.7) * self.loop_direction, self.entity.stats["move_speed"] * dt)

            else:
                dis = self.entity.dis(self.entity.unit.behavior.target) - (
                    self.entity.stats["size"] + self.entity.unit.behavior.target.stats["size"]
                )
                if dis > self.entity.stats["range"]:
                    self.entity.advance(angle, self.entity.stats["move_speed"] * dt)

                # always try to attack
                self.entity.attempt_attack(self.entity.unit.behavior.target)

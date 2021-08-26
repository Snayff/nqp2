import math
import random
from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import DEFENSE_SCALE, PUSH_FORCE, WEIGHT_SCALE
from scripts.core.utility import offset

if TYPE_CHECKING:
    from scripts.scenes.combat.elements.unit import Unit

__all__ = ["Entity"]

"""
Don't try to enforce typing with some of the functions here. They're meant to take anything with a "pos" attribute.
This can be adjusted to have valid typing, but it'd make a lot of stuff unnecessarily complicated.
"""


class Entity:
    def __init__(self, parent_unit):
        self.unit: Unit = parent_unit
        self.game = self.unit.game

        self.pos = self.unit.pos.copy()
        self.team = self.unit.team
        self.type: str = self.unit.type
        self.health: int = self.unit.health
        self.defence: int = self.unit.defence
        self.attack: int = self.unit.attack
        self.range: int = self.unit.range
        self.attack_speed: float = self.unit.attack_speed
        self.move_speed: int = self.unit.move_speed
        self.ammo: int = self.unit.ammo
        self.count: int = self.unit.count
        self.size: int = self.unit.size
        self.weight: int = self.unit.weight

        # animation stuff
        self.action = "walk"
        self.frame_timer = 0

        self.behaviour = self.game.data.behaviours.entity_behaviours[self.unit.default_behaviour](self)

        self.attack_timer = 0
        self.pushed_by_log = []
        self.pushed_log = []
        self.damaged_by_log = []

        # tracks movement from the previous frame
        self.pos_change = [0, 0]

        self.alive = True

        # slightly adjust position so the initial spread is round
        self.pos[0] += random.random() * 0.1 - 0.05  # don't use seeded rng
        self.pos[1] += random.random() * 0.1 - 0.05  # don't use seeded rng

        # temp
        self.colour = self.unit.colour

    def move(self, movement):
        """
        Splits the movement operation into smaller amounts to prevent issues with high speed movement.
        Calls the move sub-process anywhere from one to several times depending on the speed.
        """
        move_count = int(abs(movement[0]) // self.game.combat.terrain.tile_size + 1)
        move_count = max(int(abs(movement[1]) // self.game.combat.terrain.tile_size + 1), move_count)
        move_amount = [movement[0] / move_count, movement[1] / move_count]
        for i in range(move_count):
            self.sub_move(move_amount)

    def sub_move(self, movement):
        self.pos[0] += movement[0]
        if self.game.combat.terrain.check_tile_solid(self.pos):
            if movement[0] > 0:
                self.pos[0] = self.game.combat.terrain.tile_rect_px(self.pos).left - 1
            if movement[0] < 0:
                self.pos[0] = self.game.combat.terrain.tile_rect_px(self.pos).right + 1

        self.pos[1] += movement[1]
        if self.game.combat.terrain.check_tile_solid(self.pos):
            if movement[1] > 0:
                self.pos[1] = self.game.combat.terrain.tile_rect_px(self.pos).top - 1
            if movement[1] < 0:
                self.pos[1] = self.game.combat.terrain.tile_rect_px(self.pos).bottom + 1

    def dis(self, entity):
        """
        Find the distance to another entity or other object with a position.
        """
        return math.sqrt((self.pos[0] - entity.pos[0]) ** 2 + (self.pos[1] - entity.pos[1]) ** 2)

    def angle(self, entity):
        """
        Find the angle to another entity or other object with a position.
        """
        return math.atan2(entity.pos[1] - self.pos[1], entity.pos[0] - self.pos[0])

    def advance(self, angle, amount):
        movement = [math.cos(angle) * amount, math.sin(angle) * amount]
        self.move(movement)

    def deal_damage(self, amount, owner=None):
        # prevent damage if in god_mode
        if not (self.team == "player" and "god_mode" in self.game.memory.flags):
            self.health -= amount * (DEFENSE_SCALE / (DEFENSE_SCALE + self.defence))
            if self.health <= 0:
                self.health = 0
                self.alive = False

            self.damaged_by_log = (self.damaged_by_log + [owner])[-30:]

    def attempt_attack(self, entity):
        if self.attack_timer <= 0:
            self.attack_timer = 1 / self.attack_speed
            if self.dis(entity) - (entity.size + self.size) < self.range:

                # increase damage if in god_mode
                if self.team == "player" and "god_mode" in self.game.memory.flags:
                    mod = 9999
                else:
                    mod = 0

                entity.deal_damage(self.attack + mod, self)

                self.attack_timer = 1 / self.attack_speed

    def update(self, dt):
        self.frame_timer += dt
        # FIXME - temporary looping frame logic
        while self.frame_timer > 0.66:
            self.frame_timer -= 0.66

        self.attack_timer = max(0, self.attack_timer - dt)

        start_pos = self.pos.copy()

        self.behaviour.process(dt)

        self.pos_change = [self.pos[0] - start_pos[0], self.pos[1] - start_pos[1]]

        # handle collision
        for entity in self.game.combat.all_entities:
            if entity != self:
                combined_size = self.size + entity.size
                # horizontal scan
                if abs(entity.pos[0] - self.pos[0]) < combined_size:
                    # vertical scan
                    if abs(entity.pos[1] - self.pos[1]) < combined_size:
                        # full check instead of rough
                        dis = self.dis(entity)
                        if dis < combined_size:
                            # push both (pushing gets doubled)
                            angle = self.angle(entity)
                            force = 1 - dis / combined_size
                            entity.advance(
                                angle,
                                (self.weight + WEIGHT_SCALE) / (entity.weight + WEIGHT_SCALE) * dt * PUSH_FORCE * force,
                            )
                            self.advance(
                                angle + math.pi,
                                (entity.weight + WEIGHT_SCALE) / (self.weight + WEIGHT_SCALE) * dt * PUSH_FORCE * force,
                            )
                            entity.pushed_by_log = (entity.pushed_by_log + [self])[-30:]
                            self.pushed_log = (self.pushed_log + [entity])[-30:]

    @property
    def img(self):
        # temporary frame logic
        frame = int(self.frame_timer * 6)
        try:
            img = self.game.assets.unit_animations[self.type][self.action][frame]
        except KeyError:
            img = pygame.Surface((self.size * 2, self.size * 2))

        return img

    def render(self, surface: pygame.Surface, shift=(0, 0)):
        if self.type in self.game.assets.unit_animations:
            flip = False
            if self.pos_change[0] < 0:
                flip = True

            surface.blit(
                pygame.transform.flip(self.img, flip, False),
                (
                    self.pos[0] + shift[0] - self.img.get_width() // 2,
                    self.pos[1] + shift[1] - self.img.get_height() // 2,
                ),
            )
        else:
            pygame.draw.circle(surface, self.colour, offset(shift.copy(), self.pos), self.size)

        # debug stuff for swarm targeting
        # if self.behaviour.priority_target:
        #    pygame.draw.line(
        #        surface,
        #        (255, 0, 255),
        #        offset(shift.copy(), self.pos),
        #        offset(shift.copy(), self.behaviour.priority_target.pos),
        #    )
        # elif self.unit.behaviour.target:
        #    pygame.draw.line(
        #        surface,
        #        (255, 255, 0),
        #        offset(shift.copy(), self.pos),
        #        offset(shift.copy(), self.unit.behaviour.target.pos),
        #    )

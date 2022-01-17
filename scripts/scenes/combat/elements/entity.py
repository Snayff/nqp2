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
        injury_deduction = 1 - 0.1 * parent_unit.injuries

        self.unit: Unit = parent_unit
        self._game = self.unit._game

        self.pos = self.unit.pos.copy()
        self.team = self.unit.team
        self.type: str = self.unit.type
        self.health: int = int(self.unit.health * injury_deduction)
        self.defence: int = int(self.unit.defence * injury_deduction)
        self.attack: int = int(self.unit.attack * injury_deduction)
        self.range: int = self.unit.range
        self.attack_speed: float = self.unit.attack_speed * injury_deduction
        self.move_speed: int = int(self.unit.move_speed * injury_deduction)
        self.ammo: int = int(self.unit.ammo * injury_deduction)
        self.use_ammo = self.unit.ammo > 0
        self.count: int = int(self.unit.count * injury_deduction)
        self.projectile_data = self.unit.projectile_data
        self.size: int = self.unit.size
        self.weight: int = self.unit.weight

        # animation stuff
        self.action = "walk"
        self.frame_timer = 0

        self.behaviour = self._game.data.behaviours.entity_behaviours[self.unit.default_behaviour](self)

        self.attack_timer = 0
        self.pushed_by_log = []
        self.pushed_log = []
        self.damaged_by_log = []

        # tracks movement from the previous frame
        self.pos_change = [0, 0]

        self.alive = True

        self.is_attacking = False

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
        move_count = int(abs(movement[0]) // self._game.combat.terrain.tile_size + 1)
        move_count = max(int(abs(movement[1]) // self._game.combat.terrain.tile_size + 1), move_count)
        move_amount = [movement[0] / move_count, movement[1] / move_count]
        for i in range(move_count):
            self.sub_move(move_amount)

    def sub_move(self, movement):
        self.pos[0] += movement[0]
        if self._game.combat.terrain.check_tile_solid(self.pos):
            if movement[0] > 0:
                self.pos[0] = self._game.combat.terrain.tile_rect_px(self.pos).left - 1
            if movement[0] < 0:
                self.pos[0] = self._game.combat.terrain.tile_rect_px(self.pos).right + 1

        self.pos[1] += movement[1]
        if self._game.combat.terrain.check_tile_solid(self.pos):
            if movement[1] > 0:
                self.pos[1] = self._game.combat.terrain.tile_rect_px(self.pos).top - 1
            if movement[1] < 0:
                self.pos[1] = self._game.combat.terrain.tile_rect_px(self.pos).bottom + 1

    def dis(self, entity):
        """
        Find the distance to another entity or other object with a position.
        """
        return math.sqrt((self.pos[0] - entity.pos[0]) ** 2 + (self.pos[1] - entity.pos[1]) ** 2)

    def raw_dis(self, pos):
        return math.sqrt((self.pos[0] - pos[0]) ** 2 + (self.pos[1] - pos[1]) ** 2)

    def angle(self, entity):
        """
        Find the angle to another entity or other object with a position.
        """
        return math.atan2(entity.pos[1] - self.pos[1], entity.pos[0] - self.pos[0])

    def advance(self, angle, amount):
        movement = [math.cos(angle) * amount, math.sin(angle) * amount]
        self.move(movement)

    def deal_damage(self, amount, owner=None):
        # prevent damage if in godmode
        dmg_amt = 0
        if not (self.team == "player" and "godmode" in self._game.memory.flags):
            dmg_amt = amount * (DEFENSE_SCALE / (DEFENSE_SCALE + self.defence))
            self.health -= dmg_amt
            self.unit.damage_received += dmg_amt
            if self.health <= 0:
                self.health = 0
                if self.alive:
                    self.frame_timer = 0
                    self._game.combat.last_unit_death = (self, owner if owner else self)
                self.alive = False

            # comment me out to remove the hit animation
            if self.action != "death":
                self.action = "hit"
                self.frame_timer = 0

            self._game.combat.particles.create_particle_burst(self.pos.copy(), (255, 50, 100), random.randint(10, 16))

            self.damaged_by_log = (self.damaged_by_log + [owner])[-30:]

        return (self.alive, dmg_amt)

    def attempt_attack(self, entity):
        if (not self.use_ammo) or (self.ammo > 0):
            if self.dis(entity) - (entity.size + self.size) < self.range:
                self.is_attacking = True
                if self.attack_timer <= 0:
                    self.attack_timer = 1 / self.attack_speed

                # increase damage if in godmode
                if self.team == "player" and "godmode" in self._game.memory.flags:
                    mod = 9999
                else:
                    mod = 0

                if self.use_ammo:
                    self.ammo -= 1
                    self._game.combat.projectiles.add_projectile(self, entity)
                    if self.ammo <= 0:
                        # switch to melee when out of ammo
                        self.use_ammo = False
                        self.range = 0

                else:
                    dmg_status = entity.deal_damage(self.attack + mod, self)
                    if not dmg_status[0]:
                        self.unit.kills += 1
                    self.unit.damage_dealt += dmg_status[1]

                self.attack_timer = 1 / self.attack_speed

    def update(self, dt):
        self.frame_timer += dt

        self.attack_timer = max(0, self.attack_timer - dt)

        start_pos = self.pos.copy()

        # make sure the attack action can be transferred after movement
        self.is_attacking = False
        if (not self._game.combat.force_idle) and self.alive:
            self.behaviour.process(dt)

        if not self.alive:
            self.action = "death"
            self.frame_timer = min(self.frame_timer, self.cycle_length - 0.001)
        elif self.action == "hit":
            if self.frame_timer >= self.cycle_length:
                self.frame_timer = 0
                self.action = "idle"
        else:
            self.frame_timer = self.frame_timer % self.cycle_length

        self.pos_change = [self.pos[0] - start_pos[0], self.pos[1] - start_pos[1]]
        if self.action not in ["hit", "death"]:
            if sum(self.pos_change) == 0:
                self.action = "idle"
            else:
                self.action = "walk"
            if self.is_attacking:
                self.action = "attack"

        # handle collision
        if self.alive:
            for entity in self._game.world.get_all_entities():
                if (entity != self) and (entity.alive):
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
                                    (self.weight + WEIGHT_SCALE)
                                    / (entity.weight + WEIGHT_SCALE)
                                    * dt
                                    * PUSH_FORCE
                                    * force,
                                )
                                self.advance(
                                    angle + math.pi,
                                    (entity.weight + WEIGHT_SCALE)
                                    / (self.weight + WEIGHT_SCALE)
                                    * dt
                                    * PUSH_FORCE
                                    * force,
                                )
                                entity.pushed_by_log = (entity.pushed_by_log + [self])[-30:]
                                self.pushed_log = (self.pushed_log + [entity])[-30:]

    @property
    def cycle_length(self):
        if self.action == "walk":
            cycle_length = self.move_speed / 70
        elif self.action == "attack":
            cycle_length = self.attack_speed
        elif self.action == "hit":
            cycle_length = 0.3
        elif self.action == "death":
            cycle_length = 1.5
        else:
            cycle_length = 0.7
        return cycle_length

    @property
    def animation_frames(self):
        return len(self._game.assets.unit_animations[self.type][self.action])

    @property
    def img(self):
        frame = int(self.frame_timer / self.cycle_length * self.animation_frames) % self.animation_frames

        try:
            img = self._game.assets.unit_animations[self.type][self.action][frame]
        except KeyError:
            img = pygame.Surface((self.size * 2, self.size * 2))

        return img

    def render(self, surface: pygame.Surface, shift=(0, 0)):
        if self.type in self._game.assets.unit_animations:
            flip = False
            if self.pos_change[0] < 0:
                flip = True

            surface.blit(
                pygame.transform.flip(self.img, flip, False),
                (
                    self.pos[0] + shift[0] - self.img.get_width() // 2,
                    self.pos[1] + shift[1] - self.img.get_height(),
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

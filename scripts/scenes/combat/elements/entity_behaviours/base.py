import math
import random

from .behaviour import Behaviour

PATH_UPDATE_FREQ = 0.4


class Base(Behaviour):
    def complete_init(self):
        self.current_path = None
        self.movement_mode = "path"
        self.state = self.movement_mode
        self.target_unit = None
        self.target_entity = None
        self.target_pos = None
        self.visibility_line = False

        # put entities on different path update cycles
        self.last_path_update = PATH_UPDATE_FREQ * random.random()

    def walk_towards(self, point, amt):
        angle = math.atan2(point[1] - self.entity.pos[1], point[0] - self.entity.pos[0])
        self.entity.advance(angle, amt)

    def walk_path(self, dt):
        next_point = self.current_path[0]
        self.walk_towards(next_point, self.entity.move_speed * dt)
        if (
            math.sqrt((next_point[0] - self.entity.pos[0]) ** 2 + (next_point[1] - self.entity.pos[1]) ** 2)
            < self._game.combat.terrain.tile_size // 3
        ):
            self.current_path.pop(0)

    def update_target(self):
        if len(self.entity.unit.behaviour.valid_targets):
            self.target_entity = random.choice(self.entity.unit.behaviour.valid_targets)
        else:
            self.target_entity = None

    def process(self, dt):
        self.last_path_update += dt

        # check for new orders
        if self.target_unit != self.entity.unit.behaviour.target_unit:
            self.target_unit = self.entity.unit.behaviour.target_unit
            self.update_target()

        if self.target_entity:
            if (self.target_entity not in self.entity.unit.behaviour.valid_targets) or (not self.target_entity.alive):
                self.update_target()

        if self.target_entity:
            self.target_pos = self.target_entity.pos.copy()

        if self.target_entity:
            if (
                self.entity.range + self.entity.size + self.target_entity.size < self.entity.dis(self.target_entity)
            ) or (self.entity.unit.behaviour.check_visibility and not self.visibility_line):
                self.state = self.movement_mode
            else:
                self.state = "idle"

            if (not self.entity.unit.behaviour.check_visibility) or self.visibility_line:
                self.entity.attempt_attack(self.target_entity)

        if self.last_path_update > PATH_UPDATE_FREQ:
            self.last_path_update -= PATH_UPDATE_FREQ

            if self.target_entity:
                self.visibility_line = self._game.combat.terrain.sight_line(
                    self.entity.pos.copy(), self.target_entity.pos.copy()
                )
            else:
                self.visibility_line = False

            if not self.visibility_line:
                if self.entity.unit.behaviour.smart_range_retarget:
                    for entity in self._game.combat.all_entities:
                        if entity.team != self.entity.team:
                            if entity.dis(self.entity) < self.entity.range + self.entity.size + self.target_entity.size:
                                if self._game.combat.terrain.sight_line(entity.pos.copy(), self.entity.pos.copy()):
                                    self.target_entity = entity
                                    self.target_pos = self.target_entity.pos.copy()
                                    break

            if self.state == "path":
                if self.entity.unit.behaviour.regrouping:
                    self.target_pos = self.entity.unit.behaviour.leader.pos.copy()
                if self.entity.unit.behaviour.retreating:
                    self.target_pos = list(self.entity.unit.behaviour.retreat_target)
                if self.target_pos:
                    self.current_path = self._game.combat.terrain.pathfinder.px_route(
                        self.entity.pos.copy(), self.target_pos.copy()
                    )

        if self.state == "path":
            if self.current_path and len(self.current_path):
                self.walk_path(dt)

        if self.state == "straight":
            if self.target_pos:
                self.walk_towards(self.target_pos, self.entity.move_speed * dt)

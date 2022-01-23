import random

from .behaviour import Behaviour

REGROUP_RANGE = 32
RETREAT_AMT = 16


class Base(Behaviour):
    def complete_init(self):
        # these are pointers. be careful with modifying them.
        self.target_unit = None
        self.reference_entity = None
        self.valid_targets = []
        self.spread_max = self.unit.entity_spread_max
        self.force_regroup = False
        self.regrouping = False
        self.force_retreat = False
        self.retreating = False
        self.retreat_target = None
        self.position_log = []
        self.check_visibility = False
        self.smart_range_retarget = False

        # override with ranged logic when applicable
        if self.unit.use_ammo:
            self.check_visibility = True

    @property
    def leader(self):
        return self.unit.entities[0] if len(self.unit.entities) else None

    def find_target(self):
        """
        Find the nearest enemy from a different team and update the target.
        """
        nearest = [None, 9999999]
        for entity in self._game.memory.get_all_entities():
            if entity.team != self.unit.team:
                dis = entity.dis(self.unit)
                if dis < nearest[1]:
                    nearest = [entity, dis]

        if nearest[0]:
            self.target_unit = nearest[0]._parent_unit
            self.reference_entity = random.choice(nearest[0]._parent_unit.entities)
        else:
            self.target_unit = None
            self.reference_entity = None

    def update_valid_targets(self):
        self.valid_targets = []
        if self.target_unit:
            for entity in self.target_unit.entities:
                if entity.dis(self.reference_entity) < self.spread_max:
                    self.valid_targets.append(entity)

    def process(self, dt):
        if len(self.unit.entities):
            if (not self.target_unit) or (not self.target_unit.alive):
                self.find_target()

            if self.leader:
                # TODO - remove reliance on scene
                loc = self._game.world.ui.terrain.px_to_loc(self.leader.pos.copy())
                if loc not in self.position_log:
                    self.position_log.append(loc)
                    self.position_log = self.position_log[-50:]

            if self.regrouping or self.retreating:
                all_x = [e.pos[0] for e in self.unit.entities]
                all_y = [e.pos[1] for e in self.unit.entities]
                if self.retreating:
                    all_x.append(self.retreat_target[0])
                    all_y.append(self.retreat_target[1])
                if (max(all_x) - min(all_x)) < REGROUP_RANGE:
                    if (max(all_y) - min(all_y)) < REGROUP_RANGE:
                        self.regrouping = False
                        self.retreating = False
                        for entity in self.unit.entities:
                            entity.behaviour.state = entity.behaviour.movement_mode

            # update reference entity when it dies
            if self.target_unit and self.target_unit.alive and (not self.reference_entity.alive):
                if len(self.target_unit.entities):
                    self.reference_entity = random.choice(self.target_unit.entities)
                else:
                    self.target_unit = None
                    # regroup/retreat since target unit died
                    if self.force_regroup or self.force_retreat:
                        if self.force_regroup:
                            self.regrouping = True
                        if self.force_retreat:
                            self.retreating = True
                            self.retreat_target = (
                                self.position_log[-RETREAT_AMT][0] * self._game.combat.terrain.tile_size,
                                self.position_log[-RETREAT_AMT][1] * self._game.combat.terrain.tile_size,
                            )
                        for entity in self.unit.entities:
                            entity.behaviour.state = "path"
                            entity.behaviour.target_entity = None

        self.update_valid_targets()

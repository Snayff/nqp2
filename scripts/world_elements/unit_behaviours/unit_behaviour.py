from __future__ import annotations

import logging
import random
from abc import ABC

from typing import TYPE_CHECKING

import snecs

from scripts.core.components import AI, Allegiance, IsDead, Position
from scripts.core.constants import TILE_SIZE
from scripts.core.utility import distance_to

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.world_elements.unit2 import Unit2
    from snecs.typedefs import EntityID
    from scripts.core.game import Game

__all__ = ["UnitBehaviour"]


REGROUP_RANGE = 32
RETREAT_AMT = 16


class UnitBehaviour:

    def __init__(self, game: Game, unit: Unit2):
        self._game = game
        self.unit = unit
        self.target_unit: Optional[Unit2] = None
        self.reference_entity: Optional[EntityID] = None
        self.valid_targets: List = []
        self.spread_max: int = self.unit.entity_spread_max
        self.force_regroup: bool = False
        self.regrouping: bool = False
        self.force_retreat: bool = False
        self.retreating: bool = False
        self.retreat_target: Optional[Tuple[int, int]] = None
        self.position_log: List[Tuple[int, int]] = []
        self.check_visibility: bool = True if self.unit.is_ranged else False
        self.smart_range_retarget: bool = False

    @property
    def leader(self) -> EntityID:
        return self.unit.entities[0] if len(self.unit.entities) else None

    def find_target(self):
        """
        Find the nearest enemy from a different team and update the target.
        """
        nearest = [None, 9999999]
        for entity in self._game.world.model.get_all_entities():
            other_team = snecs.entity_component(entity, Allegiance).team
            if other_team != self.unit.team:
                dis = entity.dis(self.unit)
                if dis < nearest[1]:
                    nearest = [entity, dis]

        if nearest[0]:
            self.target_unit = snecs.entity_component(nearest[0], Allegiance).unit
            self.reference_entity = random.choice(self.target_unit.entities)
        else:
            self.target_unit = None
            self.reference_entity = None

    def update_valid_targets(self):
        self.valid_targets = []
        if self.target_unit:
            for entity in self.target_unit.entities:
                position = snecs.entity_component(entity, Position)
                other_position = snecs.entity_component(self.reference_entity, Position)
                if distance_to(position.pos, other_position.pos) < self.spread_max:
                    self.valid_targets.append(entity)

    def update(self, delta_time: float):
        if len(self.unit.entities):
            if (not self.target_unit) or (not self.target_unit.is_alive):
                self.find_target()

            if self.leader:
                position = snecs.entity_component(self.leader, Position)
                loc = self._game.world.model.px_to_loc(position.pos)
                if loc not in self.position_log:
                    self.position_log.append(loc)
                    self.position_log = self.position_log[-50:]

            if self.regrouping or self.retreating:
                all_x = []
                all_y = []
                for entity in self.unit.entities:
                    position = snecs.entity_component(entity, Position)
                    all_x.append(position.x)
                    all_y.append(position.y)

                if self.retreating:
                    all_x.append(self.retreat_target[0])
                    all_y.append(self.retreat_target[1])

                if (max(all_x) - min(all_x)) < REGROUP_RANGE:
                    if (max(all_y) - min(all_y)) < REGROUP_RANGE:
                        self.regrouping = False
                        self.retreating = False
                        for entity in self.unit.entities:
                            behaviour = snecs.entity_component(entity, AI).behaviour
                            behaviour.state = behaviour.movement_mode

            # update reference entity when it dies
            if self.reference_entity is None:
                ref_entity_is_alive = False
            else:
                ref_entity_is_alive = not snecs.has_component(self.reference_entity, IsDead)
            if self.target_unit and self.target_unit.is_alive and (not ref_entity_is_alive):
                # if we have possible targets pick another random one to be the reference
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
                                self.position_log[-RETREAT_AMT][0] * TILE_SIZE,
                                self.position_log[-RETREAT_AMT][1] * TILE_SIZE,
                            )
                        for entity in self.unit.entities:
                            behaviour = snecs.entity_component(entity, AI).behaviour
                            behaviour.state = "path"
                            behaviour.target_entity = None

        self.update_valid_targets()

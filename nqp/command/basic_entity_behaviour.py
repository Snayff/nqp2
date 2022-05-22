from __future__ import annotations

from typing import TYPE_CHECKING

import snecs
from snecs.typedefs import EntityID

from nqp.base_classes.entity_behaviour import EntityBehaviour
from nqp.command.unit import Unit
from nqp.core.constants import HealingSource, PATH_UPDATE_FREQ
from nqp.core.utility import distance_to
from nqp.world_elements.entity_components import Allegiance, HealReceived, IsDead, IsReadyToAttack, Position, Stats

if TYPE_CHECKING:
    from nqp.core.game import Game


__all__ = ["BasicEntityBehaviour"]


class BasicEntityBehaviour(EntityBehaviour):
    def __init__(self, game: Game, unit: Unit, entity: EntityID):
        super().__init__(game, unit, entity)

    def update(self, delta_time: float):
        self.last_path_update += delta_time

        if self.state == "path_fast":
            self.new_move_speed = 500
        else:
            self.reset_move_speed = True

        # check for new orders
        if self.target_unit != self._unit.behaviour.target_unit:
            self.target_unit = self._unit.behaviour.target_unit
            self.update_target_entity()

        if self.target_entity:
            is_alive = not snecs.has_component(self.target_entity, IsDead)
            if (self.target_entity not in self._unit.behaviour.valid_targets) or (not is_alive):
                self.update_target_entity()

            self.determine_next_action(True)

        # update path
        if self.last_path_update > PATH_UPDATE_FREQ:
            self.update_path()

        # apply and reset regen, if needed
        if self.regen_timer < 0:
            self.apply_regen()
            self.regen_timer = 1

        # update timers
        self.attack_timer -= delta_time
        self.regen_timer -= delta_time

    def determine_next_action(self, focus_entity: bool):
        """
        Determine what to do next, i.e. what state to transition into.

        If focus_entity is True then should a target position exist it
        will be overwritten by the target entity's position.
        """
        stats = snecs.entity_component(self._entity, Stats)
        pos = snecs.entity_component(self._entity, Position)
        target_stats = snecs.entity_component(self.target_entity, Stats)

        # update target pos
        if focus_entity or self.target_position is None:
            target_pos = snecs.entity_component(self.target_entity, Position).pos
            self.target_position = target_pos
        else:
            target_pos = self.target_position

        # check distance to target
        if (stats.range.value + stats.size.value + target_stats.size.value < distance_to(pos.pos, target_pos)) or (
            self._unit.behaviour.check_visibility and not self.visibility_line
        ):
            self.state = self.movement_mode
        else:
            self.state = "idle"

        # attack intent
        if ((not self._unit.behaviour.check_visibility) or self.visibility_line) and self.attack_timer <= 0:
            # ensure doesnt al ready have component
            if not snecs.has_component(self._entity, IsReadyToAttack):
                snecs.add_component(self._entity, IsReadyToAttack())

    def update_path(self):
        """
        Update pathing to target.
        """
        # decrement timer
        self.last_path_update -= PATH_UPDATE_FREQ

        # check if can see target
        if self.target_entity:
            pos = snecs.entity_component(self._entity, Position)
            target_pos = snecs.entity_component(self.target_entity, Position)
            self.visibility_line = self._game.world.model.terrain.sight_line(pos.pos, target_pos.pos)
        else:
            self.visibility_line = False

        # if we cant see target, move somewhere new
        if not self.visibility_line:
            if self._unit.behaviour.smart_range_retarget:
                team = snecs.entity_component(self._entity, Allegiance).team
                stats = snecs.entity_component(self._entity, Stats)
                pos = snecs.entity_component(self._entity, Position)
                for entity in self._game.world.model.get_all_entities():
                    target_team = snecs.entity_component(entity, Allegiance).team

                    # find entities on different team
                    if target_team != team:
                        target_pos = snecs.entity_component(self.target_entity, Position)
                        target_stats = snecs.entity_component(entity, Stats)

                        # check if in range
                        if stats.range.value + stats.size.value + target_stats.size.value < distance_to(
                            pos.pos, target_pos.pos
                        ):

                            # check target is visible
                            if self._game.world.model.terrain.sight_line(target_pos.pos, pos.pos):

                                # new target found, update info and stop searching
                                self.target_entity = entity
                                self.target_position = target_pos.pos
                                break

        if self.state == "path" or self.state == "path_fast":
            if self._unit.behaviour.regrouping:
                self.target_position = self._unit.behaviour.leader.pos
            if self._unit.behaviour.retreating:
                self.target_position = list(self._unit.behaviour.retreat_target)
            if self.target_position:
                pos = snecs.entity_component(self._entity, Position)
                self.current_path = self._game.world.model.terrain.pathfind_px(pos.pos, self.target_position)

    def apply_regen(self):
        """
        Create heal component on entity
        """
        stats = snecs.entity_component(self._entity, Stats)

        # try to apply
        try:
            snecs.add_component(self._entity, HealReceived(stats.regen.value, HealingSource.SELF))

        except ValueError:
            heal_received = snecs.entity_component(self._entity, HealReceived)
            heal_received.add_heal(stats.regen.value, HealingSource.SELF)

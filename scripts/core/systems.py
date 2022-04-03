from __future__ import annotations

import logging
import math

from typing import TYPE_CHECKING

import pygame
import snecs
from snecs.typedefs import EntityID

from scripts.core import queries
from scripts.core.definitions import PointLike
from scripts.core.components import AI, Aesthetic, Allegiance, DamageReceived, IsDead, Position, RangedAttack, Stats
from scripts.core.constants import EntityFacing, TILE_SIZE
from scripts.core.utility import angle_to, distance_to

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.core.game import Game

__all__ = ["draw_entities", "apply_damage", "process_death"]


def draw_entities(surface: pygame.Surface, shift: Tuple[int, int] = (0, 0)):
    """
    Draw all entities
    """
    for entity, (position, aesthetic) in queries.aesthetic_position:
        if aesthetic.facing == EntityFacing.LEFT:
            flip = True
        else:
            flip = False

        animation = aesthetic.animation

        surface.blit(
            pygame.transform.flip(animation.surface, flip, False),
            (
                position.x + shift[0] - animation.width // 2,  # TODO - why minus width and height?
                position.y + shift[1] - animation.height)
        )


def apply_damage():
    """
    Consume damage components and apply their value to the Entity.
    """
    for entity, (damage, resources) in queries.damage_resources:
        resources.health.value -= damage

        # remove damage
        snecs.remove_component(entity, DamageReceived)

        # check if dead
        if resources.health.value <= 0:
            snecs.add_component(entity, IsDead())


def process_death():
    """
    Update Entity's sprites and intentions.
    """
    for entity, (dead, aesthetic) in queries.dead_aesthetic:

        # update to dead sprite
        aesthetic.animation.set_current_frame_set_name("death")
        aesthetic.animation.delete_on_finish = False
        aesthetic.animation.loop = False


def process_movement(delta_time: float, game: Game):
    """
    Update an Entity's position towards their target.
    """
    for entity, (position, stats, ai) in queries.position_stats_ai_not_dead:

        move_result = _walk_path(delta_time, position, stats, ai, game)

        # update facing
        if snecs.has_component(entity, Aesthetic):
            aesthetic = snecs.entity_component(entity, Aesthetic)
            if move_result[0][0] < move_result[1][0]:
                facing = EntityFacing.LEFT
            else:
                facing = EntityFacing.RIGHT
            aesthetic.facing = facing


def _walk_path(
        delta_time: float,
        position: Position,
        stats: Stats,
        ai: AI,
        game: Game
) -> List[Tuple[int, int], Tuple[int, int]]:
    """
    Have entity walk along their path.

    Returns [start_pos. new_pos].
    """
    next_point = ai.behaviour.current_path[0]
    angle = angle_to(position.pos, next_point)
    move_distance = stats.move_speed.value * delta_time
    movement = [math.cos(angle) * move_distance, math.sin(angle) * move_distance]
    move_results = _move(movement, position, game)

    # if we reached next point on the path then remove from list
    if distance_to(position.pos, next_point) < TILE_SIZE // 3:  # TODO - why over 3?
        ai.behaviour.current_path.pop(0)

    return move_results


def _move(movement: PointLike, position: Position, game: Game) -> List[Tuple[int, int], Tuple[int, int]]:
    """
    Splits the movement operation into smaller amounts to prevent issues with high speed movement.
    Calls the move sub-process anywhere from one to several times depending on the speed.

    Returns [start_pos. new_pos].
    """
    move_count = int(abs(movement[0]) // TILE_SIZE + 1)
    move_count = max(int(abs(movement[1]) // TILE_SIZE + 1), move_count)
    move_amount = [movement[0] / move_count, movement[1] / move_count]
    start_pos = position.pos
    new_pos = start_pos
    for i in range(move_count):
        new_pos = _sub_move(move_amount, position, game)

    return [start_pos, new_pos]


def _sub_move(movement: PointLike, position: Position, game: Game) -> Tuple[int, int]:
    """
    Small movement. Returns end position.
    """
    check_tile_solid = game.world.model.terrain.check_tile_solid
    tile_rect_px = game.world.model.terrain.tile_rect_px

    position.x += movement[0]
    if check_tile_solid(position.pos):
        if movement[0] > 0:
            position.pos.x = tile_rect_px(position.pos).left - 1
        if movement[0] < 0:
            position.pos.x = tile_rect_px(position.pos).right + 1

    position.pos.y += movement[1]
    if check_tile_solid(position.pos):
        if movement[1] > 0:
            position.pos.y = tile_rect_px(position.pos).top - 1
        if movement[1] < 0:
            position.pos.y = tile_rect_px(position.pos).bottom + 1

    return position.pos


def process_ai(delta_time: float):
    """
    Update Entity ai.
    """
    for entity, (ai,) in queries.ai_not_dead:
        ai.behaviour.process(delta_time)

        # check if behaviour flags need processing
        if ai.behaviour.new_move_speed is not None:
            if snecs.has_component(entity, Stats):
                stats = snecs.entity_component(entity, Stats)
                stats.move_speed = ai.behaviour.new_move_speed

                ai.behaviour.new_move_speed = None

        if ai.behaviour.reset_move_speed:
            if snecs.has_component(entity, Stats):
                stats = snecs.entity_component(entity, Stats)
                stats.move_speed.reset()


def process_attack(game: Game):
    """
    Execute any outstanding attacks.
    """
    for entity, (attack_flag, position, stats, ai) in queries.attack_position_stats_ai_not_dead:
        add_projectile = game.world.model.projectiles.add_projectile

        # check we have someone to target
        if ai.behaviour.target_entity is None:
            continue

        # check that someone has the details we need
        target_entity = ai.behaviour.target_entity
        if not snecs.has_component(target_entity, Stats):
            continue

        stats = snecs.entity_component(entity, Stats)
        target_pos = snecs.entity_component(target_entity, Position)
        target_stats = snecs.entity_component(target_entity, Stats)

        # check in range
        in_range = distance_to(position.pos, target_pos.pos) - (target_stats.size.value + stats.size.value)
        if in_range < stats.range.value:

            # handle ranged attack
            if snecs.has_component(entity, RangedAttack):
                ranged = snecs.entity_component(entity, RangedAttack)
                ranged.ammo.value -= 1
                add_projectile(entity, target_entity)

                # switch to melee when out of ammo
                if ranged.ammo.value <= 0:
                    stats.range.value = 0

            else:

                # increase damage if in godmode
                mod = 0
                if "godmode" in game.memory.flags:
                    if snecs.has_component(entity, Allegiance):
                        if snecs.entity_component(entity, Allegiance).team == "player":
                            mod = 9999

                # add damage component
                snecs.add_component(target_entity, DamageReceived(stats.attack.value + mod))

            # reset attack timer
            ai.behaviour.attack_timer = 1 / stats.attack_speed.value



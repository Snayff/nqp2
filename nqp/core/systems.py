from __future__ import annotations

import logging
import math
import random
from typing import TYPE_CHECKING

import pygame
import snecs

from nqp.core import queries
from nqp.core.constants import (
    CRIT_MOD,
    DamageType,
    EntityFacing,
    Flags,
    HealingSource,
    PUSH_FORCE,
    TILE_SIZE,
    WEIGHT_SCALE,
)
from nqp.core.utility import angle_to, distance_to, get_direction
from nqp.world_elements.entity_components import (
    AI,
    Allegiance,
    DamageReceived,
    HealReceived,
    IsDead,
    IsReadyToAttack,
    Position,
    RangedAttack,
    Stats,
)

if TYPE_CHECKING:
    from typing import List

    from nqp.core.game import Game

__all__ = ["draw_entities", "apply_damage", "process_death"]


def draw_entities(surface: pygame.Surface, shift: pygame.Vector2 = (0, 0)):
    """
    Draw all entities
    """
    draw_list = list()

    # organize entities for layered rendering
    for entity, (aesthetic, position) in queries.aesthetic_position:
        flip = aesthetic.facing == EntityFacing.LEFT
        animation = aesthetic.animation
        frame = pygame.transform.flip(animation.surface, flip, False)
        # animation frame offset b/c entity's position is where their feet are
        x = position.x + shift.x - animation.width // 2
        y = position.y + shift.y - animation.height
        draw_list.append((position.y, x, y, len(draw_list), frame))

    # sort so entities higher on the screen are drawn first (painters alg)
    draw_list.sort()
    for operation in draw_list:
        _, x, y, _, frame = operation
        surface.blit(frame, (x, y))


def apply_damage(game: Game):
    """
    Consume damage components and apply their value to the Entity, applying any mitigations.
    Dodge may negate damage.
    """
    for entity, (damage, aesthetic, stats) in queries.damage_aesthetic_stats:
        damage_dealt = damage.amount

        # get defence
        if damage.type == DamageType.MAGICAL:
            defence = stats.magic_defence
        elif damage.type == DamageType.MUNDANE:
            defence = stats.mundane_defence
        else:
            logging.warning(f"Damage type ({damage.type.name}) not recognised. Defaulted to mundane defence.")
            defence = stats.mundane_defence

        # crit ignores defence
        if not damage.is_crit:

            # mitigate damage by defence, accounting for penetration
            damage_dealt = max((defence.value - damage.penetration) - damage_dealt, 0)

        # calc dodge
        dodge_successful = False
        if game.rng.roll() <= stats.dodge.value:
            dodge_successful = True

        # apply hit effects if no dodge
        if dodge_successful:
            # reduce defence for being hit
            defence.base_value = max(defence.value - 1, 0)

            # apply damage
            stats.health.base_value -= damage_dealt

            # check if dead
            if stats.health.value <= 0:
                snecs.add_component(entity, IsDead())
            else:
                # apply flash
                aesthetic.animation.flash((255, 255, 255))

                # create blood spray on crit
                if damage.is_crit:
                    position = snecs.entity_component(entity, Position)
                    game.world.model.particles.create_blood_spray()

        # remove damage flag
        snecs.remove_component(entity, DamageReceived)


def process_death(game: Game):
    """
    Update Entity's sprites and intentions.
    """

    for entity, (dead, aesthetic, position) in queries.dead_aesthetic_position:

        # update to dead sprite
        aesthetic.animation.set_current_frame_set_name("death")
        aesthetic.animation.delete_on_finish = False
        aesthetic.animation.loop = False

        game.world.model.particles.create_blood_spray(position.pos)


def process_movement(delta_time: float, game: Game):
    """
    Update an Entity's position towards their target.
    """
    for entity, (position, stats, ai, aesthetic) in queries.position_stats_ai_aesthetic_not_dead:

        # skip if we have nowhere to go
        if ai.behaviour.current_path is None:
            continue
        if len(ai.behaviour.current_path) == 0:
            continue
        if ai.behaviour.is_active == False:
            continue
        if ai.behaviour.state not in ["path", "path_fast"]:
            continue
        if ai.behaviour.state == "path_fast":
            stats.move_speed.override(100)
        elif ai.behaviour.state == "path":
            stats.move_speed.reset()

        move_result = _walk_path(delta_time, position, stats, ai, game)

        # update facing
        if move_result[0][0] < move_result[1][0]:
            facing = EntityFacing.LEFT
        else:
            facing = EntityFacing.RIGHT
        aesthetic.facing = facing

        # update sprite frame set
        aesthetic.animation.set_current_frame_set_name("move")


def _walk_path(
    delta_time: float, position: Position, stats: Stats, ai: AI, game: Game
) -> List[pygame.Vector2, pygame.Vector2]:
    """
    Have entity walk along their path.

    Returns [start_pos. new_pos].
    """
    next_point = ai.behaviour.current_path[0]
    angle = angle_to(position.pos, next_point)
    move_distance = stats.move_speed.value * delta_time
    movement = get_direction(angle, move_distance)
    move_results = _move(movement, position, game)

    # if we reached next point on the path then remove from list
    if distance_to(position.pos, next_point) < TILE_SIZE // 3:  # TODO - why over 3?
        ai.behaviour.current_path.pop(0)

    return move_results


def _move(movement: pygame.Vector2, position: Position, game: Game) -> List[pygame.Vector2, pygame.Vector2]:
    """
    Splits the movement operation into smaller amounts to prevent issues with high speed movement.
    Calls the move sub-process anywhere from one to several times depending on the speed.

    Returns [start_pos. new_pos].
    """
    move_count = int(abs(movement[0]) // TILE_SIZE + 1)
    move_count = max(int(abs(movement[1]) // TILE_SIZE + 1), move_count)
    move_amount = pygame.Vector2(movement[0] / move_count, movement[1] / move_count)
    start_pos = position.pos
    new_pos = start_pos
    for i in range(move_count):
        new_pos = _sub_move(move_amount, position, game)

    return [start_pos, new_pos]


def _sub_move(movement: pygame.Vector2, position: Position, game: Game) -> pygame.Vector2:
    """
    Small movement. Returns end position.
    """
    check_tile_solid = game.world.model.terrain.check_tile_solid
    tile_rect_px = game.world.model.terrain.tile_rect_px

    position.x += movement[0]
    if check_tile_solid(position.pos):
        if movement[0] > 0:
            position.x = tile_rect_px(position.pos).left - 1
        if movement[0] < 0:
            position.x = tile_rect_px(position.pos).right + 1

    position.y += movement[1]
    if check_tile_solid(position.pos):
        if movement[1] > 0:
            position.y = tile_rect_px(position.pos).top - 1
        if movement[1] < 0:
            position.y = tile_rect_px(position.pos).bottom + 1

    return position.pos


def process_ai(delta_time: float):
    """
    Update Entity ai.
    """
    for entity, (ai,) in queries.ai_not_dead:
        ai.behaviour.update(delta_time)

        # check if behaviour flags need processing
        if ai.behaviour.new_move_speed is not None:
            if snecs.has_component(entity, Stats):
                stats = snecs.entity_component(entity, Stats)
                stats.move_speed.override(ai.behaviour.new_move_speed)
                ai.behaviour.new_move_speed = None

        if ai.behaviour.reset_move_speed:
            if snecs.has_component(entity, Stats):
                stats = snecs.entity_component(entity, Stats)
                stats.move_speed.reset()


def process_attack(game: Game):
    """
    Execute any outstanding attacks.
    """
    for entity, (attack_flag, position, stats, ai, aesthetic) in queries.attack_position_stats_ai_aesthetic_not_dead:
        add_projectile = game.world.model.projectiles.add_projectile

        # check we have someone to target
        if ai.behaviour.target_entity is None:
            continue

        # check that someone has the details we need
        target_entity = ai.behaviour.target_entity
        if not snecs.has_component(target_entity, Stats):
            continue

        target_pos = snecs.entity_component(target_entity, Position)
        target_stats = snecs.entity_component(target_entity, Stats)

        # check in range
        in_range = distance_to(position.pos, target_pos.pos) - (target_stats.size.value + stats.size.value)
        if in_range < stats.range.value:

            # update to attack animation
            aesthetic.animation.set_current_frame_set_name("attack")

            # increase damage if in godmode
            mod = 0
            if game.memory.check_for_flag(Flags.GODMODE):
                if snecs.has_component(entity, Allegiance):
                    if snecs.entity_component(entity, Allegiance).team == "player":
                        mod = 9999

            # roll for crit
            is_crit = False
            if stats.crit_chance.value > game.rng.roll():
                mod += CRIT_MOD
                is_crit = True

            # handle ranged attack
            if snecs.has_component(entity, RangedAttack):
                ranged = snecs.entity_component(entity, RangedAttack)
                ranged.ammo.base_value -= 1
                projectile_data = {"img": ranged.projectile_sprite, "speed": ranged.projectile_speed}
                add_projectile(entity, target_entity, projectile_data, stats.attack.value * mod)

                # switch to melee when out of ammo
                if ranged.ammo.value <= 0:
                    stats.range.override(0)

            else:
                # add damage component
                snecs.add_component(
                    target_entity,
                    DamageReceived(stats.attack.value * mod, stats.damage_type, stats.penetration.value, is_crit),
                )

            # reset attack timer and remove flag
            ai.behaviour.attack_timer = 1 / stats.attack_speed.value
            snecs.remove_component(entity, IsReadyToAttack)


def push_entities_away_from_one_another(delta_time: float, game: Game):
    """
    Force overlapping units away from one another.
    """
    for entity, (position, stats) in queries.position_stats_not_dead:

        for other_entity, (other_position, other_stats) in queries.position_stats_not_dead:
            combined_size = stats.size.value + other_stats.size.value

            # horizontal scan
            if abs(other_position.x - position.x) < combined_size:
                # vertical scan
                if abs(other_position.y - position.y) < combined_size:

                    # check distance
                    distance = distance_to(position.pos, other_position.pos)
                    if distance < combined_size:

                        # push other away from entity
                        angle = angle_to(position.pos, other_position.pos)
                        force = 1 - distance / combined_size
                        move_distance = (
                            (stats.weight.value + WEIGHT_SCALE)
                            / (other_stats.weight.value + WEIGHT_SCALE)
                            * delta_time
                            * PUSH_FORCE
                            * force
                        )
                        movement = get_direction(angle, move_distance)
                        _move(movement, other_position, game)

                        # push entity away from other
                        other_angle = angle + math.pi  # TODO - why + pi?
                        move_distance = (
                            (other_stats.weight.value + WEIGHT_SCALE)
                            / (stats.weight.value + WEIGHT_SCALE)
                            * delta_time
                            * PUSH_FORCE
                            * force
                        )
                        movement = get_direction(other_angle, move_distance)
                        _move(movement, position, game)


def process_healing():
    """
    Process all the Healing Received components, applying healing where allowed.
    """
    for entity, (healing_received, stats, attributes) in queries.heal_stats_attributes_not_dead:
        for heal in healing_received.heals:
            amount, source = heal

            if (source == HealingSource.SELF and attributes.can_be_healed_by_self) or (
                source == HealingSource.OTHER and attributes.can_be_healed_by_other
            ):
                stats.health.base_value += amount

        # remove component
        snecs.remove_component(entity, HealReceived)

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import pygame
import snecs

from scripts.core import queries
from scripts.core.components import Aesthetic, DamageReceived, IsDead
from scripts.core.constants import EntityFacing

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

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
        resources.health -= damage

        # remove damage
        snecs.remove_component(entity, DamageReceived)

        # check if dead
        if resources.health <= 0:
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


def process_movement():
    """
    Update an Entity's position towards their target.
    """
    for entity, (position,) in queries.position:


        # update facing
        if snecs.has_component(entity, Aesthetic):
            aesthetic = snecs.entity_component(entity, Aesthetic)
            if move_x < 0:
                facing = EntityFacing.LEFT
            else:
                facing = EntityFacing.RIGHT
            aesthetic.facing = facing


def process_ai(delta_time: float):
    """
    Update Entity ai.
    """
    for entity, (ai,) in queries.ai_not_dead:
        ai.behaviour.process(delta_time)




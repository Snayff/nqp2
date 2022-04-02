from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import pygame
import snecs

from scripts.core import queries
from scripts.core.components import DamageReceived, IsDead

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["draw_entities", "apply_damage", "process_death"]


def draw_entities(surface: pygame.Surface, shift: Tuple[int, int] = (0, 0)):
    """
    Draw all entities
    """
    for entity, (position, aesthetic) in queries.aesthetic_position:
        surface.blit(aesthetic.surface, (position.x + shift[0], position.y + shift[1]))


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
    for entity, (dead, knowledge, aesthetic, position) in queries.dead_knowledge_aesthetic_position:
        # set target to current pos
        knowledge.target_pos = position.pos

        # update to dead sprite
        aesthetic.animation.set_current_frame_set_name("death")
        aesthetic.animation.delete_on_finish = False
        aesthetic.animation.loop = False





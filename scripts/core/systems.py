from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import pygame
import snecs

from scripts.core import queries
from scripts.core.components import DamageReceived, IsDead

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["draw_entities"]


def draw_entities(surface: pygame.Surface):
    """
    Draw all entities
    """
    for entity, (position, aesthetic) in queries.aesthetic_position:
        surface.blit(aesthetic.surface, (position.x, position.y))



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







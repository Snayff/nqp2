from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from snecs import RegisteredComponent
from snecs.typedefs import EntityID

from scripts.core.base_classes.animation import Animation
from scripts.core.base_classes.image import Image
from scripts.core.constants import EntityFacing
from scripts.world_elements.entity_behaviours.entity_behaviour import EntityBehaviour
from scripts.world_elements.stat import FloatStat, IntStat
from scripts.world_elements.unit2 import Unit2

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["Position", "Aesthetic", "Tracked", "Resources", "Stats", "Allegiance", "AI", "RangedAttack",
    "DamageReceived", "IsDead", "IsReadyToAttack"]


class Position(RegisteredComponent):
    """
    An Entity's location in the world. 
    """
    def __init__(self, pos: Tuple[int, int]):
        self.pos: Tuple[int, int] = pos

    def serialize(self):
        return self.pos

    @classmethod
    def deserialize(cls, pos: Tuple[int, int]):
        return Position(pos)
    
    @property
    def x(self) -> int:
        return self.pos[0]

    @x.setter
    def x(self, value: int):
        self.pos = (value, self.pos[1])

    @property
    def y(self) -> int:
        return self.pos[1]

    @y.setter
    def y(self, value: int):
        self.pos = (self.pos[0], value)


class Aesthetic(RegisteredComponent):
    """
    An Entity's visual information
    """
    def __init__(self, animation: Animation):
        self.animation: Animation = animation
        self.facing: EntityFacing = EntityFacing.RIGHT

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Aesthetic(*serialised)
    
    
class Tracked(RegisteredComponent):
    """
    A component to track an entity's actions. 
    """
    def __init__(self):
        pass

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Tracked(*serialised)


class Resources(RegisteredComponent):
    """
    An Entity's resources, such as health. 
    """
    def __init__(self, health: int):
        self.health: IntStat = IntStat(health)

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Resources(*serialised)


class Stats(RegisteredComponent):
    """
    An Entity's stats, such as attack. 
    """
    def __init__(self, parent_unit: Unit2):
        self.defence: IntStat = IntStat(parent_unit.defence)
        self.attack: IntStat = IntStat(parent_unit.attack)
        self.range: IntStat = IntStat(parent_unit.range)
        self.attack_speed: FloatStat = FloatStat(parent_unit.attack_speed)
        self.move_speed: IntStat = IntStat(parent_unit.move_speed)
        self.size: IntStat = IntStat(parent_unit.size)
        self.weight: IntStat = IntStat(parent_unit.weight)

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Resources(*serialised)

    
class Allegiance(RegisteredComponent):
    """
    An Entity's allegiance.
    """
    def __init__(self, team: str, unit: Unit2):
        self.team: str = team
        self.unit: Unit2 = unit

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Allegiance(*serialised)


class AI(RegisteredComponent):
    """
    An Entity's AI. This should handle the outputs of AI decisions and actions.
    """
    def __init__(self, behaviour: EntityBehaviour):
        self.behaviour: EntityBehaviour = behaviour

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        return AI()


class RangedAttack(RegisteredComponent):
    """
    An Entity's ability to use projectiles.
    """
    def __init__(self, ammo: int, projectile_sprite: Image, projectile_speed: int):
        self.ammo: IntStat = IntStat(ammo)
        self.projectile_sprite: Image = projectile_sprite
        self.projectile_speed: int = projectile_speed

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Allegiance(*serialised)


class DamageReceived(RegisteredComponent):
    """
    Damage to be applied to the Entity.
    """
    def __init__(self, amount: int):
        self.amount: int = amount

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Allegiance(*serialised)


class IsDead(RegisteredComponent):
    """
    Flag to indicate if the Entity is dead.
    """
    def __init__(self):
        self.is_processed: bool = False

    # doesnt need serialising as will never be dead when saving.


class IsReadyToAttack(RegisteredComponent):
    """
    Flag to indicate if the Entity is ready to attack.
    """
    # doesnt need init as has no details
    # doesnt need serialising as will never be about to attack when saving.

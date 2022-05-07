from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, List, Any

import pygame
from snecs import RegisteredComponent

from nqp.base_classes.animation import Animation
from nqp.base_classes.image import Image
from nqp.command.unit import Unit
from nqp.core.constants import EntityFacing, DamageType
from nqp.world_elements.stats import FloatStat, IntStat

if TYPE_CHECKING:
    from typing import Tuple

    from nqp.command.basic_entity_behaviour import BasicEntityBehaviour

__all__ = [
    "Position",
    "Aesthetic",
    "Tracked",
    "Resources",
    "Stats",
    "Allegiance",
    "AI",
    "RangedAttack",
    "DamageReceived",
    "IsDead",
    "IsReadyToAttack",
]


@dataclasses.dataclass
class StatValue:
    value: Any
    type: Any
    modified: bool
    layers: List[Any]
    base_value: Any


class Position(RegisteredComponent):
    """
    An Entity's location in the world.
    """

    def __init__(self, pos: pygame.Vector2):
        self.pos: pygame.Vector2 = pos

    def serialize(self):
        return self.pos

    @classmethod
    def deserialize(cls, pos: pygame.Vector2):
        return Position(pos)

    @property
    def x(self) -> int:
        return int(self.pos.x)

    @x.setter
    def x(self, value: int):
        self.pos = pygame.Vector2(value, self.pos.y)

    @property
    def y(self) -> int:
        return int(self.pos.y)

    @y.setter
    def y(self, value: int):
        self.pos = pygame.Vector2(self.pos.x, value)


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

    def __init__(self, parent_unit: Unit):
        self.mundane_defence: IntStat = IntStat(parent_unit.mundane_defence)
        self.magic_defence: IntStat = IntStat(parent_unit.magic_defence)
        self.attack: IntStat = IntStat(parent_unit.attack)
        self.damage_type: DamageType = DamageType[parent_unit.damage_type.upper()]
        self.range: IntStat = IntStat(parent_unit.range)
        self.attack_speed: FloatStat = FloatStat(parent_unit.attack_speed)
        self.move_speed: IntStat = IntStat(parent_unit.move_speed)
        self.size: IntStat = IntStat(parent_unit.size)
        self.weight: IntStat = IntStat(parent_unit.weight)
        self.penetration: IntStat = IntStat(parent_unit.penetration)
        self.crit_chance: IntStat = IntStat(parent_unit.crit_chance)

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Resources(*serialised)

    @classmethod
    def get_stat_names(cls) -> List[str]:
        """
        Get a list of all the stats.
        """
        stat_attrs = [
            "mundane_defence",
            "magic_defence",
            "attack",
            "damage_type",
            "range",
            "attack_speed",
            "move_speed",
            "size",
            "weight",
            "penetration",
            "crit_chance",
        ]
        return stat_attrs


class Allegiance(RegisteredComponent):
    """
    An Entity's allegiance.
    """

    def __init__(self, team: str, unit: Unit):
        self.team: str = team
        self.unit: Unit = unit

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

    def __init__(self, behaviour: BasicEntityBehaviour):
        self.behaviour: BasicEntityBehaviour = behaviour

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

    def __init__(self, amount: int, damage_type: DamageType, penetration: int, is_crit: bool):
        self.amount: int = amount
        self.type: DamageType = damage_type
        self.penetration: int = penetration
        self.is_crit: bool = is_crit

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

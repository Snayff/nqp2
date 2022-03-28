from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from snecs import RegisteredComponent

from scripts.core.base_classes.animation import Animation
from scripts.core.base_classes.image import Image
from scripts.scene_elements.unit import Unit

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["Position"]


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

    @property
    def y(self) -> int:
        return self.pos[1]
        

class Visual(RegisteredComponent):
    """
    An Entity's visual information
    """
    def __init__(self, animation: Animation):
        self.animation: Animation = animation

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Visual(*serialised)
    
    
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
        self.health: int = health

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
        self.defence: int = parent_unit.defence
        self.attack: int = parent_unit.attack
        self.range: int = parent_unit.range
        self.attack_speed: float = parent_unit.attack_speed
        self.move_speed: int = parent_unit.move_speed

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Resources(*serialised)
    
    
class IsAlive(RegisteredComponent):
    """
    An Entity's state of being alive. Acts as a flag.
    """
    def __init__(self):
        pass

    def serialize(self):
        return True

    @classmethod
    def deserialize(cls, *serialised):
        return IsAlive()
    
    
class Team(RegisteredComponent):
    """
    An Entity's team. 
    """
    def __init__(self, team: str):
        self.team: str = team

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Team(*serialised)


class Intent(RegisteredComponent):
    """
    An Entity's Intent, such as were they are moving to or when they last attacked.

    This should handle the outputs of AI decisions.
    """
    def __init__(self):
        self.attack_timer: float = 0
        self.target_pos: Optional[Tuple[int, int]] = None  # where the entity is moving to


    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        return Intent()


class UsesProjectiles(RegisteredComponent):
    """
    An Entity's ability to use projectiles.
    """
    def __init__(self, ammo: int, projectile_sprite: Image, projectile_speed: int):
        self.ammo: int = ammo
        self.projectile_sprite: Image = projectile_sprite
        self.projectile_speed: int = projectile_speed

    def serialize(self):
        # TODO - add serialisation
        return True

    @classmethod
    def deserialize(cls, *serialised):
        # TODO - add deserialisation
        return Team(*serialised)
from __future__ import annotations
from enum import auto, IntEnum

__all__ = ["VERSION", "INFINITE"]

VERSION: str = "0.0.1"


INFINITE: int = 999

class CombatState:
    CHOOSE_CARD = auto()
    SELECT_TARGET = auto()
    WATCH = auto()

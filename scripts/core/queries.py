from __future__ import annotations

import logging
from importlib import resources

from typing import TYPE_CHECKING

from snecs import Query

from scripts.core.components import Aesthetic, DamageReceived, IsDead, Behaviour, Position, Resources

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["dead", "resources", "aesthetic_position", "damage_resources", ]

resources = Query([Resources]).compile()

dead = Query([IsDead]).compile()

position = Query([Position]).compile()

aesthetic_position = Query([Aesthetic, Position]).compile()

damage_resources = Query([DamageReceived, Resources]).compile()

dead_aesthetic_position = Query([IsDead, Aesthetic, Position]).compile()


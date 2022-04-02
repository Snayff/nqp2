from __future__ import annotations

import logging
from importlib import resources

from typing import TYPE_CHECKING

from snecs import Query

from scripts.core.components import Aesthetic, DamageReceived, IsDead, Knowledge, Position, Resources

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["dead", "resources", "aesthetic_position", "damage_resources", "dead_knowledge_aesthetic_position"]

resources = Query([Resources]).compile()

dead = Query([IsDead]).compile()

aesthetic_position = Query([Aesthetic, Position]).compile()

damage_resources = Query([DamageReceived, Resources]).compile()

dead_knowledge_aesthetic_position = Query([IsDead, Knowledge, Aesthetic, Position]).compile()


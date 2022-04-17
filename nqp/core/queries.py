from __future__ import annotations

import logging
from importlib import resources
from typing import TYPE_CHECKING

from snecs import Query

from nqp.core.components import Aesthetic, AI, DamageReceived, IsDead, IsReadyToAttack, Position, Resources, Stats

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = [
    "dead",
    "resources",
    "aesthetic_position",
    "damage_resources_aesthetic",
    "ai_not_dead",
    "attack_position_stats_ai_aesthetic_not_dead",
    "ai_position",
]

resources = Query([Resources]).compile()

dead = Query([IsDead]).compile()

position = Query([Position]).compile()

ai_position = Query([AI, position]).compile()

ai_not_dead = Query([AI]).filter(~IsDead).compile()

aesthetic_position = Query([Aesthetic, Position]).compile()

damage_resources_aesthetic = Query([DamageReceived, Resources, Aesthetic]).compile()

dead_aesthetic_position = Query([IsDead, Aesthetic, Position]).compile()

position_stats_not_dead = Query([Position, Stats]).filter(~IsDead).compile()

position_stats_ai_aesthetic_not_dead = Query([Position, Stats, AI, Aesthetic]).filter(~IsDead).compile()

attack_position_stats_ai_aesthetic_not_dead = (
    Query([IsReadyToAttack, Position, Stats, AI, Aesthetic]).filter(~IsDead).compile()
)

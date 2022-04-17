from __future__ import annotations

from typing import TYPE_CHECKING

from snecs import Query

from nqp.core.components import Aesthetic, AI, DamageReceived, IsDead, IsReadyToAttack, Position, Resources, Stats

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union, Iterator
    from snecs.typedefs import EntityID

__all__ = [
    "dead",
    "resources",
    "aesthetic_position",
    "damage_resources_aesthetic_stats",
    "ai_not_dead",
    "attack_position_stats_ai_aesthetic_not_dead",
    "ai_position",
]

resources: Iterator[Tuple[EntityID, Tuple[Resources]]] = Query([Resources]).compile()

dead: Iterator[Tuple[EntityID, Tuple[IsDead]]] = Query([IsDead]).compile()

position: Iterator[Tuple[EntityID, Tuple[Position]]] = Query([Position]).compile()

ai_position: Iterator[Tuple[EntityID, Tuple[AI, Position]]] = Query([AI, position]).compile()

ai_not_dead: Iterator[Tuple[EntityID, Tuple[AI]]] = Query([AI]).filter(~IsDead).compile()

aesthetic_position: Iterator[Tuple[EntityID, Tuple[Aesthetic, Position]]] = Query([Aesthetic, Position]).compile()

damage_resources_aesthetic_stats: Iterator[Tuple[EntityID, Tuple[DamageReceived, Resources, Aesthetic,
                                                                 Stats]]] = Query(
    [DamageReceived, Resources, Aesthetic, Stats]).compile()

dead_aesthetic_position: Iterator[Tuple[EntityID, Tuple[IsDead, Aesthetic, Position]]] = Query(
    [IsDead, Aesthetic, Position]).compile()

position_stats_not_dead: Iterator[Tuple[EntityID, Tuple[Position, Stats]]] = Query(
    [Position, Stats]).filter(~IsDead).compile()

position_stats_ai_aesthetic_not_dead: Iterator[Tuple[EntityID, Tuple[Position, Stats, AI, Aesthetic]]] = Query(
    [Position, Stats, AI, Aesthetic]).filter(~IsDead).compile()

attack_position_stats_ai_aesthetic_not_dead: Iterator[Tuple[EntityID, Tuple[IsReadyToAttack, Position, Stats, AI,
                                                                            Aesthetic]]] = (
    Query([IsReadyToAttack, Position, Stats, AI, Aesthetic]).filter(~IsDead).compile())


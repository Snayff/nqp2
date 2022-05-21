from __future__ import annotations

from typing import TYPE_CHECKING

from snecs import Query

from nqp.effects.effect_components import StatsEffect, StatsEffectSentinel
from nqp.effects.processors import EffectProcessorComponent
from nqp.world_elements.entity_components import (
    Aesthetic,
    AI,
    DamageReceived,
    IsDead,
    IsReadyToAttack,
    Position,
    Resources,
    Stats,
)

if TYPE_CHECKING:
    from typing import Iterator, Tuple

    from snecs.typedefs import EntityID

__all__ = [
    "dead",
    "resources",
    "aesthetic_position",
    "damage_resources_aesthetic_stats",
    "ai_not_dead",
    "attack_position_stats_ai_aesthetic_not_dead",
    "ai_position",
    "position",
    "ai_position",
    "dead_aesthetic_position",
    "position_stats_not_dead",
    "position_stats_ai_aesthetic_not_dead",
    "effects_processors",
    "stats_query",
    "effect_stats_query",
    "sentinels_query",
]

resources: Iterator[Tuple[EntityID, Tuple[Resources]]]
resources = Query([Resources]).compile()

dead: Iterator[Tuple[EntityID, Tuple[IsDead]]]
dead = Query([IsDead]).compile()

position: Iterator[Tuple[EntityID, Tuple[Position]]]
position = Query([Position]).compile()

ai_position: Iterator[Tuple[EntityID, Tuple[AI, Position]]]
ai_position = Query([AI, position]).compile()

ai_not_dead: Iterator[Tuple[EntityID, Tuple[AI]]]
ai_not_dead = Query([AI]).filter(~IsDead).compile()

aesthetic_position: Iterator[Tuple[EntityID, Tuple[Aesthetic, Position]]]
aesthetic_position = Query([Aesthetic, Position]).compile()

damage_resources_aesthetic_stats: Iterator[Tuple[EntityID, Tuple[DamageReceived, Resources, Aesthetic, Stats]]]
damage_resources_aesthetic_stats = Query([DamageReceived, Resources, Aesthetic, Stats]).compile()

dead_aesthetic_position: Iterator[Tuple[EntityID, Tuple[IsDead, Aesthetic, Position]]]
dead_aesthetic_position = Query([IsDead, Aesthetic, Position]).compile()

position_stats_not_dead: Iterator[Tuple[EntityID, Tuple[Position, Stats]]]
position_stats_not_dead = Query([Position, Stats]).filter(~IsDead).compile()

position_stats_ai_aesthetic_not_dead: Iterator[Tuple[EntityID, Tuple[Position, Stats, AI, Aesthetic]]]
position_stats_ai_aesthetic_not_dead = Query([Position, Stats, AI, Aesthetic]).filter(~IsDead).compile()

attack_position_stats_ai_aesthetic_not_dead: Iterator[
    Tuple[EntityID, Tuple[IsReadyToAttack, Position, Stats, AI, Aesthetic]]
]
attack_position_stats_ai_aesthetic_not_dead = (
    Query([IsReadyToAttack, Position, Stats, AI, Aesthetic]).filter(~IsDead).compile()
)

effects_processors: Iterator[Tuple[EntityID, Tuple[EffectProcessorComponent]]]
effects_processors = Query([EffectProcessorComponent]).compile()

stats_query: Iterator[Tuple[EntityID, Tuple[Stats]]]
stats_query = Query([Stats]).compile()

effect_stats_query: Iterator[Tuple[EntityID, Tuple[StatsEffect, Stats]]]
effect_stats_query = Query([StatsEffect, Stats]).compile()

sentinels_query: Iterator[Tuple[EntityID, Tuple[StatsEffectSentinel]]]
sentinels_query = Query([StatsEffectSentinel]).compile()

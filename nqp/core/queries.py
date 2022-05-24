from __future__ import annotations

from typing import TYPE_CHECKING

from snecs import Query

from nqp.effects.effect_components import StatsEffect, StatsEffectSentinel
from nqp.effects.processors import EffectProcessorComponent
from nqp.world_elements.entity_components import (
    Aesthetic,
    AI,
    Attributes,
    DamageReceived,
    HealReceived,
    IsDead,
    IsReadyToAttack,
    Position,
    Stats,
)

if TYPE_CHECKING:
    from typing import Iterator, Tuple

    from snecs.typedefs import EntityID

__all__ = [
    "aesthetic_position",
    "ai_not_dead",
    "ai_position",
    "attack_position_stats_ai_aesthetic_not_dead",
    "damage_aesthetic_stats",
    "dead",
    "dead_aesthetic_position",
    "effect_stats_query",
    "effects_processors",
    "heal_stats_attributes_not_dead",
    "position",
    "position_stats_not_dead",
    "position_stats_ai_aesthetic_not_dead",
    "sentinels_query",
    "stats_query",
]

heal_stats_attributes_not_dead: Iterator[Tuple[EntityID, Tuple[HealReceived, Stats, Attributes]]]
heal_stats_attributes_not_dead = Query([HealReceived, Stats, Attributes]).filter(~IsDead).compile()

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

damage_aesthetic_stats: Iterator[Tuple[EntityID, Tuple[DamageReceived, Aesthetic, Stats]]]
damage_aesthetic_stats = Query([DamageReceived, Aesthetic, Stats]).compile()

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

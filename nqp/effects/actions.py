from __future__ import annotations

import operator
from functools import partial
from typing import TYPE_CHECKING

import snecs
from snecs.typedefs import EntityID

from nqp.base_classes.stat import Stat
from nqp.core.constants import INFINITE
from nqp.core.utility import percent_to_float
from nqp.world_elements.entity_components import Stats

if TYPE_CHECKING:
    from typing import List


def get_modifier(string: str):
    if string.endswith("%"):
        return partial(operator.mul, percent_to_float(string))
    else:
        string = string.lstrip("+")
        return lambda x: float(string)


def new_stats_effect(
    stat: Stat,
    stats: Stats,
    modifier: str,
    ttl: float = INFINITE,
) -> EntityID:
    """
    Apply StatsEffect to Stat

    Args:
        stat: Stat instance to modify
        stats: Stats Component containing ``stat``
        modifier: Modifier string; "50%", "-50", "-200%", etc
        ttl: Time To Live

    """
    modifier = get_modifier(modifier)
    from nqp.effects.effect_components import StatsEffect

    attrib_modifier = StatsEffect(stat, ttl)
    eid = snecs.new_entity((attrib_modifier, stats))
    stat.apply_modifier(modifier, attrib_modifier)
    return eid


def apply_effects(entities: List[EntityID]):
    """
    Enable effects for entity by checking the sentinels.

    Should be called whenever a new entity or sentinel is created.

    New entities may be created after an effect was started.  This can
    be used to search for effects that would affect the entity and apply
    them.

    """
    # TODO: get components from sentinel and batch search
    from nqp.world_elements.entity_components import Allegiance, Stats

    search_components = (Allegiance, Stats)
    from nqp.core.queries import sentinels_query

    for sentinel_eid, (sentinel,) in sentinels_query:
        for eid in entities:
            components = snecs.entity_components(eid, search_components)
            sentinel.maybe_apply(components[Allegiance], components[Stats])

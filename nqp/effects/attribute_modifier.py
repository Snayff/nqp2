from __future__ import annotations

import operator
import uuid
from functools import partial
from typing import TYPE_CHECKING, Dict, Any, Iterator, Tuple, List

import snecs
from snecs.typedefs import EntityID

from nqp.base_classes.stat import Stat
from nqp.core.components import Stats, Allegiance
from nqp.core.effect import EffectProcessor
from nqp.core.utility import percent_to_float

if TYPE_CHECKING:
    from nqp.core.game import Game


def get_modifier(string: str):
    if string.endswith("%"):
        return partial(operator.mul, percent_to_float(string))
    else:
        string = string.lstrip("+")
        return lambda x: float(string)


class StatsEffect(snecs.RegisteredComponent):
    """
    Currently, only modifying ``Stats`` components is supported

    Args:
        target: Stat instance to modify
        ttl: Time To Live

    ttl:
         -1 : never removed
          0 : runs once
        > 0 : lasts X seconds

    """

    def __init__(self, target: Any, ttl: float = -1):
        self.target: Any = target
        self.ttl: float = ttl


class StatsEffectSentinel(snecs.RegisteredComponent):
    """
    Fancy way to search for targets of an effect

    """

    def __init__(self, target, unit_type, attribute, modifier, params, ttl: float = -1):
        self.target = target
        self.unit_type = unit_type
        self.attribute = attribute
        self.modifier = get_modifier(modifier)
        self.params = params
        self.ttl = ttl
        self.key = uuid.uuid4()

    @classmethod
    def from_dict(cls, data: Dict[str, str], params: Dict):
        """
        Return new instance using data loaded from a file

        """
        target = data.get("target")
        unit_type = data.get("unit_type")
        attribute = data.get("attribute")
        modifier = data.get("modifier")
        ttl = float(data.get("ttl", -1))

        if target not in ("all", "game", "self", "team", "unit"):
            raise ValueError(f"Unsupported target {target}")
        if unit_type not in ("all", "ranged"):
            raise ValueError(f"Unsupported unit_type {unit_type}")

        return cls(target, unit_type, attribute, modifier, params, ttl)

    def test(self, allg: Allegiance):
        if self.target == "all":
            pass
        elif self.target == "team" and allg.team != self.params["team"]:
            return False
        elif self.target == "unit" and allg.unit != self.params["unit"]:
            return False
        if self.unit_type == "all":
            pass
        return True


stats_query: Iterator[Tuple[EntityID, Tuple[StatsEffect, Stats]]]
stats_query = snecs.Query([StatsEffect, Stats])
sentinels_query: Iterator[Tuple[EntityID, Tuple[StatsEffectSentinel]]]
sentinels_query = snecs.Query([StatsEffectSentinel])


def enable_new_effects_from_sentinels(entities: List[EntityID]):
    """
    Enable effects for entity by checking the sentinels

    Call this after creating an entity and the correct effects will be applied

    """
    # TODO: move queries to the sentinel
    search_components = (Allegiance, Stats)
    for sentinel_eid, (sentinel,) in sentinels_query:
        for eid in entities:
            components = snecs.entity_components(eid, search_components)
            allg: Allegiance = components[Allegiance]
            stats: Stats = components[Stats]
            if sentinel.test(allg):
                stat = getattr(stats, sentinel.attribute, None)
                if stat is None or not isinstance(stat, Stat):
                    raise ValueError(f"Unsupported attribute {sentinel.attribute}")
                if not stat.has_modifier(sentinel.key):
                    stat.apply_modifier(sentinel.modifier, sentinel.key)
                    attrib_modifier = StatsEffect(stat)
                    snecs.new_entity((attrib_modifier, stats))


def new_sentinel(**kwargs):
    sentinel = StatsEffectSentinel(**kwargs)
    eid = snecs.new_entity((sentinel,))
    sentinel.key = eid
    return sentinel


def new_stats_effect(
    stat: Stat,
    stats: Stats,
    modifier: str,
    ttl: float = -1,
) -> StatsEffect:
    """
    Apply effect to Stats

    """
    modifier = get_modifier(modifier)
    attrib_modifier = StatsEffect(stat, ttl)
    eid = snecs.new_entity((attrib_modifier, stats))
    stat.apply_modifier(modifier, eid)
    return attrib_modifier


def enable_effect(effect: StatsEffectSentinel, params: Dict[str:str]):
    """
    Scan for targets that match and directly apply modifier

    Currently, only modifying ``Stats`` components is supported

    """
    if effect.target == "game":
        raise NotImplementedError
    elif effect.target == "self":
        raise NotImplementedError
    else:
        # search for matching targets
        for allg, stats in search_stats(effect.target, effect.unit_type, params):
            stat = getattr(stats, effect.attribute, None)
            if stat is None or not isinstance(stat, Stat):
                raise ValueError(f"Unsupported attribute {effect.attribute}")
            if not stat.has_modifier(effect.key):
                stat.apply_modifier(modifier, effect.key)
                attrib_modifier = StatsEffect(stat)
                snecs.new_entity((attrib_modifier, stats))


def search_stats(
    target: str,
    unit_type: str,
    params: Dict[str:str],
) -> Iterator[Allegiance, Stats]:
    """
    Iterate targets that match

    """

    for eid, (allg, stats) in snecs.Query([Allegiance, Stats]):
        if target == "all":
            pass
        elif target == "team" and allg.team != params["team"]:
            break
        elif target == "unit" and allg.unit != params["unit"]:
            break
        if unit_type == "all":
            pass
        elif allg.unit.type != unit_type:
            break
        yield allg, stats


class StatsEffectProcessor(EffectProcessor):
    """
    Processor for Effects

    * Remove expired effects

    """

    def update(self, time_delta: float, game: Game):
        # handle each modifier
        for eid, (effect, stats) in stats_query:
            # TODO: check if eid was seen last scan, but no longer seen
            # remove expired modifiers
            if effect.ttl == -1:
                continue
            if effect.ttl >= 0:
                effect.ttl -= time_delta
                if effect.ttl <= 0:
                    effect.target.remove_modifier(eid)
                    snecs.schedule_for_deletion(eid)

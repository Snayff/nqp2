from __future__ import annotations

import operator
import uuid
from functools import partial
from typing import TYPE_CHECKING

import snecs
from snecs.typedefs import EntityID

from nqp.base_classes.stat import Stat
from nqp.core.components import Allegiance, Stats
from nqp.core.effect import EffectProcessor
from nqp.core.utility import percent_to_float

if TYPE_CHECKING:
    from typing import Any, Dict, Iterator, List, Optional, Tuple

    from nqp.core.game import Game


def get_modifier(string: str):
    if string.endswith("%"):
        return partial(operator.mul, percent_to_float(string))
    else:
        string = string.lstrip("+")
        return lambda x: float(string)


class StatsEffect(snecs.RegisteredComponent):
    """
    Currently, only modifying ``Stats`` components are supported

    Args:
        stat: Stat instance on the Stats component
        ttl: Time To Live

    ttl:
         -1 : never removed
          0 : runs once
        > 0 : lasts X seconds

    """

    def __init__(self, stat: Any, ttl: float = -1):
        self.stat: Any = stat
        self.ttl: float = ttl


class StatsEffectSentinel(snecs.RegisteredComponent):
    """
    Fancy way to search for targets of an effect

    """

    def __init__(
        self,
        target: str,
        unit_type: str,
        attribute: str,
        modifier: str,
        params: Optional[Dict[str:Any]] = None,
        ttl: float = -1,
    ):
        if params is None:
            params = dict()
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

        Args:
            data: Dictionary of generic params, probably from a file
            params: Dictionary of data unique to the context

        For params, consider an effect which would affect the users
        "team".  We cannot know which team that is in the data files,
        since it is only known when the effect is created.  So the
        ``params`` dictionary is required to get the team value when
        the effect is created.  See ``maybe_apply``.

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

    def maybe_apply(self, allg: Allegiance, stats: Stats):
        """
        Match and test modifier.  Apply if needed.

        """
        if self.target == "all":
            pass
        elif self.target == "team" and allg.team != self.params["team"]:
            return False
        elif self.target == "unit" and allg.unit != self.params["unit"]:
            return False
        if self.unit_type == "all":
            pass
        elif self.unit_type != allg.unit.type:
            return False
        stat = getattr(stats, self.attribute, None)
        if stat is None or not isinstance(stat, Stat):
            raise ValueError(f"Unsupported attribute {self.attribute}")
        if not stat.has_modifier(self.key):
            stat.apply_modifier(self.modifier, self.key)
            attrib_modifier = StatsEffect(stat)
            snecs.new_entity((attrib_modifier, stats))


def new_stats_effect(
    stat: Stat,
    stats: Stats,
    modifier: str,
    ttl: float = -1,
) -> EntityID:
    """
    Apply StatsEffect to Stat

    Args:
        stat: Stat instance to modify
        stats: Stats Component containing ``stat``
        modifier: Modifier string; "50%", "-50". "-200%", etc
        ttl: Time To Live

    """
    modifier = get_modifier(modifier)
    attrib_modifier = StatsEffect(stat, ttl)
    eid = snecs.new_entity((attrib_modifier, stats))
    stat.apply_modifier(modifier, attrib_modifier)
    return eid


stats_query: Iterator[Tuple[EntityID, Tuple[Stats]]]
stats_query = snecs.Query([Stats])
effect_stats_query: Iterator[Tuple[EntityID, Tuple[StatsEffect, Stats]]]
effect_stats_query = snecs.Query([StatsEffect, Stats])
sentinels_query: Iterator[Tuple[EntityID, Tuple[StatsEffectSentinel]]]
sentinels_query = snecs.Query([StatsEffectSentinel])


def apply_effects(entities: List[EntityID]):
    """
    Enable effects for entity by checking the sentinels

    New entities may be created after an effect was started.  This can
    be used to search for effects that would affect the entity and apply
    them.

    """
    # TODO: get components from sentinel and batch search
    search_components = (Allegiance, Stats)
    for sentinel_eid, (sentinel,) in sentinels_query:
        for eid in entities:
            components = snecs.entity_components(eid, search_components)
            sentinel.maybe_apply(components[Allegiance], components[Stats])


class StatsEffectProcessor(EffectProcessor):
    """
    Processor for Effects

    * Remove expired effects

    """

    def update(self, time_delta: float, game: Game):
        for eid, (effect, stats) in effect_stats_query:
            # remove expired modifiers
            if effect.ttl == -1:
                continue
            if effect.ttl >= 0:
                effect.ttl -= time_delta
                if effect.ttl <= 0:
                    effect.stat.remove_modifier(effect)
                    snecs.schedule_for_deletion(eid)

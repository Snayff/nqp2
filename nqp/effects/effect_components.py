from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

import snecs
from snecs import RegisteredComponent

from nqp.base_classes.stat import Stat
from nqp.effects.actions import get_modifier
from nqp.world_elements.entity_components import Allegiance, Stats

__all__ = ["AddItemEffect", "StatsEffect", "StatsEffectSentinel"]


class AddItemEffect(RegisteredComponent):
    def __init__(self, item_type: str, item_count: int, trigger=None):
        self.item_type = item_type
        self.item_count: int = item_count
        self.trigger = trigger

    @classmethod
    def from_dict(cls, data: Dict[str, str], params: Dict[str:Any]):
        """
        Return new instance using data loaded from a file

        """
        item_type = data.get("item_type")
        if item_type not in ["gold"]:
            raise ValueError(f"Unsupported item_type {item_type}")
        trigger = data.get("trigger")
        if trigger not in ["EnterNewRoom"]:
            raise ValueError(f"Unsupported unit_type {trigger}")
        item_count = int(data.get("item_count"))
        return cls(item_type, item_count, trigger)


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

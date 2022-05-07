from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import snecs
from snecs import RegisteredComponent

from nqp.core.components import Stats
from nqp.core.effect import EffectProcessor
from nqp.core.utility import percent_to_float

if TYPE_CHECKING:
    from nqp.core.game import Game


class AttributeModifierEffect(RegisteredComponent):
    def __init__(self, target: str, unit_type: str, attribute: str, mod_amount: float):
        self.target = target
        self.unit_type = unit_type
        self.attribute = attribute
        self.mod_amount = mod_amount

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        """
        Return new instance using data loaded from a file

        """
        target = data.get("target")
        if target == "unit":
            pass
        elif target == "all":
            pass
        elif target == "game":
            pass
        else:
            raise ValueError(f"Unsupported target {target}")
        unit_type = data.get("unit_type")
        if unit_type == "ranged":
            pass
        elif unit_type == "all":
            pass
        else:
            raise ValueError(f"Unsupported unit_type {unit_type}")
        attribute = data.get("attribute")
        if attribute not in ["attack"]:
            raise ValueError(f"Unsupported attribute {attribute}")
        # TODO: consider more way to express values besides %
        mod_amount = percent_to_float(data.get("mod_amount"))
        return cls(target, unit_type, attribute, mod_amount)


class AttributeModifierEffectProcessor(EffectProcessor):
    q = snecs.Query([Stats, AttributeModifierEffect])

    def tick(self, time_delta: float, game: Game):
        for eid, (position, stats) in AttributeModifierEffectProcessor.q:
            print("fuckiii")

from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

import snecs
from snecs import RegisteredComponent

from nqp.core.effect import EffectProcessor

if TYPE_CHECKING:
    from nqp.core.game import Game


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


class AddItemEffectProcessor(EffectProcessor):
    queued_items = snecs.Query([AddItemEffect])

    def update(self, time_delta: float, game: Game):
        for eid, (comp,) in list(AddItemEffectProcessor.queued_items):
            pass

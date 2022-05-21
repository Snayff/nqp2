from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nqp.core.game import Game

log = logging.getLogger(__name__)

__all__ = ["EffectProcessor"]


class EffectProcessor(ABC):
    def update(self, time_delta: float, game: Game):
        """
        Handle changes for this Processor

        For example:
            for eid, (burn,) in list(OnFireStatusSystem.burning):
                burn.ttl -= time_delta

        """
        pass

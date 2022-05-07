from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from snecs import RegisteredComponent

if TYPE_CHECKING:
    from nqp.core.game import Game

log = logging.getLogger(__name__)


class EffectProcessorComponent(RegisteredComponent):
    def __init__(self, effect: EffectProcessor):
        self.effect = effect


class EffectProcessor:
    def tick(self, time_delta: float, game: Game):
        """
        Handle changes for this Processor

        For example:
            for eid, (burn,) in list(OnFireStatusSystem.burning):
                burn.ttl -= time_delta

        """
        pass

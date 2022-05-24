"""

not in design docs, just testing.  maybe use later?

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import snecs
from snecs import RegisteredComponent

from nqp.base_classes.effect_processor import EffectProcessor

if TYPE_CHECKING:
    from nqp.core.game import Game


class OnFireStatusEffect(RegisteredComponent):
    def __init__(self, ttl=100):
        self.ttl = ttl


class OnFireStatusProcessor(EffectProcessor):
    burning = snecs.Query([OnFireStatusEffect])

    def update(self, time_delta: float, game: Game):
        for eid, (burn,) in list(OnFireStatusProcessor.burning):
            burn.ttl -= time_delta
            if burn.ttl <= 0:
                snecs.remove_component(eid, OnFireStatusEffect)

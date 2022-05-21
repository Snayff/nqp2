from __future__ import annotations

from typing import TYPE_CHECKING

import snecs
from snecs import RegisteredComponent

from nqp.base_classes.effect_processor import EffectProcessor
from nqp.effects.effect_components import AddItemEffect

if TYPE_CHECKING:
    from nqp.core.game import Game


__all__ = ["EffectProcessorComponent", "AddItemEffectProcessor", "StatsEffectProcessor"]


class EffectProcessorComponent(RegisteredComponent):
    def __init__(self, effect: EffectProcessor):
        self.effect = effect


class AddItemEffectProcessor(EffectProcessor):
    queued_items = snecs.Query([AddItemEffect])

    def update(self, time_delta: float, game: Game):
        for eid, (comp,) in list(AddItemEffectProcessor.queued_items):
            pass


class StatsEffectProcessor(EffectProcessor):
    """
    Processor for Effects

    * Remove expired effects

    """

    def update(self, time_delta: float, game: Game):
        from nqp.core.queries import effect_stats_query

        for eid, (effect, stats) in effect_stats_query:
            # remove expired modifiers
            if effect.ttl == -1:
                continue
            if effect.ttl >= 0:
                effect.ttl -= time_delta
                if effect.ttl <= 0:
                    effect.stat.remove_modifier(effect)
                    snecs.schedule_for_deletion(eid)

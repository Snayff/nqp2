import logging
from typing import Any, Dict

log = logging.getLogger(__name__)


class Effect:
    @classmethod
    def from_dict(cls, **parameters):
        instance = cls(**parameters)
        return instance


# TODO: replace with plugins =================================================
from scripts.core.effects.add_item import AddItemEffect
from scripts.core.effects.attribute_modifier import AttributeModifierEffect
from scripts.core.effects.sildreths_signature import SildrethsSignatureEffect

effect_classes: Dict[str, Any] = dict()
for klass in (
    AddItemEffect,
    AttributeModifierEffect,
    SildrethsSignatureEffect,
):
    effect_classes[str(klass.__name__)] = klass


# ============================================================================


def load_effect(data: Dict[str, str]):
    name = data.pop("name")
    klass = effect_classes[name]
    effect = klass.from_dict(**data)
    return effect

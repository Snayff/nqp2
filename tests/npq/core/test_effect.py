import unittest
from unittest import mock

import snecs

from nqp.core.components import Position, Aesthetic, Resources, Stats, Allegiance
from nqp.core.data import Data
from nqp.core.effect import EffectProcessorComponent
from nqp.effects.attribute_modifier import AttributeModifierEffect
from nqp.effects.burn import OnFireStatusEffect

data = Data(mock.Mock())


class EffectTestCase(unittest.TestCase):
    """
    Very rough and dirty test to check for major breaks

    """

    def test_no_errors(self):
        self.game = mock.Mock()
        self.mock_stats = mock.Mock()
        self.mock_unit = mock.Mock()
        self.mock_unit.damage_type = "mundane"
        components = [
            Position(None),
            Aesthetic(None),
            Resources(None),
            Stats(self.mock_unit),
            Allegiance("team", self.mock_unit),
        ]
        item = data.create_item("albroms_item")
        self.entity_id = snecs.new_entity(components)
        snecs.add_component(self.entity_id, OnFireStatusEffect())
        snecs.add_component(self.entity_id, AttributeModifierEffect(None, None, None, None))
        query = snecs.Query((EffectProcessorComponent,))
        for _, (effect_system,) in query:
            effect_system: EffectProcessorComponent
            effect_system.effect.tick(1000, self.game)

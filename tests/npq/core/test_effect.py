import unittest
from unittest import mock

import snecs

from nqp.core import queries
from nqp.core.components import Position, Aesthetic, Resources, Stats, Allegiance
from nqp.core.data import Data
from nqp.effects.attribute_modifier import (
    StatsEffectSentinel,
    enable_effect,
    new_stats_effect,
    enable_new_effects_from_sentinels,
)
from nqp.effects.burn import OnFireStatusEffect


class EffectTestCase(unittest.TestCase):
    """
    Very rough and dirty test to check for major breaks

    """

    def setUp(self) -> None:
        # clear existing world
        snecs.ecs.move_world(snecs.World())
        self.data = Data(mock.Mock())
        self.game = mock.Mock()
        self.mock_stats = mock.Mock()
        self.mock_unit = mock.Mock(team="myteam", type="ranged")
        self.mock_unit.attack_speed = 1.0
        self.mock_unit.damage_type = "mundane"
        self.stats = Stats(self.mock_unit)
        components = [
            Position(None),
            Aesthetic(None),
            Resources(None),
            self.stats,
            Allegiance("myteam", self.mock_unit),
        ]
        self.entity_id = snecs.new_entity(components)

    def test_sentinel_from_dict(self):
        sentinel = StatsEffectSentinel.from_dict(
            data=dict(
                target="team",
                unit_type="ranged",
                attribute="attack_speed",
                modifier="50%",
            ),
            params={"team": "myteam"},
        )

    def test_attribute_modifier_timeout(self):
        """
        effect should be removed after an update
        """
        new_stats_effect(
            stat=self.stats.attack_speed,
            stats=self.stats,
            modifier="50%",
            ttl=1,
        )
        for _, (effect_system,) in queries.effects_processors:
            effect_system.effect.update(10, self.game)
        self.assertEqual(1.0, self.stats.attack_speed.value)

    def test_multiply_modifier(self):
        new_stats_effect(
            stat=self.stats.attack_speed,
            stats=self.stats,
            modifier="50%",
        )
        self.assertEqual(1.5, self.stats.attack_speed.value)

    def test_addition_modifier(self):
        new_stats_effect(
            stat=self.stats.attack_speed,
            stats=self.stats,
            modifier="50",
        )
        self.assertEqual(51, self.stats.attack_speed.value)

    def test_sentinels(self):
        sentinel = StatsEffectSentinel(
            target="team",
            unit_type="ranged",
            attribute="attack_speed",
            modifier="50%",
            params={"team": "myteam"},
        )
        snecs.new_entity((sentinel,))
        enable_new_effects_from_sentinels([self.entity_id])
        self.assertEqual(1.5, self.stats.attack_speed.value)

    def test_item_no_errors(self):
        item = self.data.create_item("albroms_item")
        item = self.data.create_item("bragans_item")
        # item = self.data.create_item("lurents_item")
        # item = self.data.create_item("ralnaths_item")
        # item = self.data.create_item("sildreths_item")
        # item = self.data.create_item("thracks_item")

    def test_fire(self):
        snecs.add_component(self.entity_id, OnFireStatusEffect())
        self.assertTrue(snecs.has_component(self.entity_id, OnFireStatusEffect))
        for _, (effect_system,) in queries.effects_processors:
            effect_system.effect.update(1000, self.game)
        self.assertFalse(snecs.has_component(self.entity_id, OnFireStatusEffect))

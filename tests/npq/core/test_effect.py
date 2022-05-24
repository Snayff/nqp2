import unittest
from unittest import mock

import snecs

from nqp.core import queries
from nqp.core.data import Data
from nqp.effects.actions import apply_effects, new_stats_effect
from nqp.effects.burn import OnFireStatusEffect
from nqp.effects.effect_components import StatsEffectSentinel
from nqp.world_elements.entity_components import Aesthetic, Allegiance, Position, Stats


class EffectTestCase(unittest.TestCase):
    """
    Very rough and dirty test to check for major breaks

    """

    def setUp(self) -> None:
        # clear existing world
        snecs.ecs.move_world(snecs.World())
        self.data = Data(mock.Mock())
        self.game = mock.Mock()
        # unit 0
        self.unit0 = mock.Mock(team="team0", type="ranged")
        self.unit0.attack_speed = 1.0
        self.unit0.damage_type = "mundane"
        self.stats0 = Stats(self.unit0)
        components = [
            Position(None),
            Aesthetic(None),
            self.stats0,
            Allegiance("team0", self.unit0),
        ]
        self.entity_id0 = snecs.new_entity(components)
        # unit 1
        self.unit1 = mock.Mock(team="team0", type="not-ranged")
        self.unit1.attack_speed = 1.0
        self.unit1.damage_type = "mundane"
        self.stats1 = Stats(self.unit0)
        components = [
            Position(None),
            Aesthetic(None),
            self.stats1,
            Allegiance("team1", self.unit1),
        ]
        self.entity_id1 = snecs.new_entity(components)

    def tick(self, dt=1000):
        for _, (effect_system,) in queries.effects_processors:
            effect_system.effect.update(dt, self.game)

    def test_sentinel_from_dict(self):
        sentinel = StatsEffectSentinel.from_dict(
            data=dict(
                target="team",
                unit_type="ranged",
                attribute="attack_speed",
                modifier="50%",
            ),
            params={"team": "team0"},
        )
        self.assertEqual("team", sentinel.target)
        self.assertEqual("ranged", sentinel.unit_type)
        self.assertEqual("attack_speed", sentinel.attribute)
        self.assertEqual({"team": "team0"}, sentinel.params)

    def test_attribute_modifier_timeout(self):
        """
        effect should be removed after an update
        """
        new_stats_effect(
            stat=self.stats0.attack_speed,
            stats=self.stats0,
            modifier="50%",
            ttl=1,
        )
        self.tick()
        self.assertEqual(1.0, self.stats0.attack_speed.value)

    def test_multiply_modifier(self):
        new_stats_effect(
            stat=self.stats0.attack_speed,
            stats=self.stats0,
            modifier="50%",
        )
        self.assertEqual(1.5, self.stats0.attack_speed.value)

    def test_addition_modifier(self):
        new_stats_effect(
            stat=self.stats0.attack_speed,
            stats=self.stats0,
            modifier="50",
        )
        self.assertEqual(51, self.stats0.attack_speed.value)

    def test_sentinels_match_team(self):
        sentinel = StatsEffectSentinel(
            target="team",
            unit_type="ranged",
            attribute="attack_speed",
            modifier="50%",
            params={"team": "team0"},
        )
        snecs.new_entity((sentinel,))
        apply_effects([self.entity_id0, self.entity_id1])
        self.assertEqual(1.5, self.stats0.attack_speed.value)
        self.assertEqual(1.0, self.stats1.attack_speed.value)

    def test_sentinels_match_unit_type(self):
        sentinel = StatsEffectSentinel(
            target="all",
            unit_type="ranged",
            attribute="attack_speed",
            modifier="50%",
        )
        snecs.new_entity((sentinel,))
        apply_effects([self.entity_id0, self.entity_id1])
        self.assertEqual(1.5, self.stats0.attack_speed.value)
        self.assertEqual(1.0, self.stats1.attack_speed.value)

    def test_removing_entity_removes_modifier(self):
        eid = new_stats_effect(
            stat=self.stats0.attack_speed,
            stats=self.stats0,
            modifier="50",
        )
        self.assertEqual(51, self.stats0.attack_speed.value)
        snecs.delete_entity_immediately(eid)
        self.assertEqual(1, self.stats0.attack_speed.value)

    def test_item_no_errors(self):
        item = self.data.create_item("albroms_item")
        item = self.data.create_item("bragans_item")
        item = self.data.create_item("lurents_item")
        item = self.data.create_item("ralnaths_item")
        item = self.data.create_item("sildreths_item")
        item = self.data.create_item("thracks_item")

    def test_fire(self):
        snecs.add_component(self.entity_id0, OnFireStatusEffect())
        self.assertTrue(snecs.has_component(self.entity_id0, OnFireStatusEffect))
        self.tick()
        self.assertFalse(snecs.has_component(self.entity_id0, OnFireStatusEffect))

import operator
import unittest
from functools import partial
from unittest import mock

from nqp.core.data import Data
from nqp.world_elements.entity_components import Stats

data = Data(mock.Mock())


class StatsTestCase(unittest.TestCase):
    def setUp(self):
        self.parent = mock.Mock(
            mundane_defence=1,
            magic_defence=1,
            attack=1,
            damage_type="mundane",
            range=1,
            attack_speed=1.0,
            move_speed=1,
            size=1,
            weight=1,
            penetration=1,
            crit_chance=1,
        )
        self.stats = Stats(self.parent)

    def test_unmodified(self):
        self.assertEqual(1, self.stats.attack_speed.value)

    def test_increase(self):
        self.stats.attack_speed.apply_modifier(partial(operator.mul, 0.50), 0)
        self.assertEqual(1.5, self.stats.attack_speed.value)

    def test_decrease(self):
        self.stats.attack_speed.apply_modifier(partial(operator.mul, -0.50), 0)
        self.assertEqual(0.5, self.stats.attack_speed.value)

    def test_apply_and_remove_single(self):
        self.stats.attack_speed.apply_modifier(partial(operator.mul, 0.50), 0)
        self.assertEqual(1.5, self.stats.attack_speed.value)
        self.stats.attack_speed.remove_modifier(0)
        self.assertEqual(1.0, self.stats.attack_speed.value)

    def test_apply_and_remove_many(self):
        self.stats.attack_speed.apply_modifier(partial(operator.mul, 0.50), 0)
        self.assertEqual(1.5, self.stats.attack_speed.value)
        self.stats.attack_speed.apply_modifier(partial(operator.mul, 0.25), 1)
        self.assertEqual(1.75, self.stats.attack_speed.value)
        self.stats.attack_speed.remove_modifier(0)
        self.assertEqual(1.25, self.stats.attack_speed.value)
        self.stats.attack_speed.remove_modifier(1)
        self.assertEqual(1.0, self.stats.attack_speed.value)

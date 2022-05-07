import unittest
from unittest import mock

from nqp.core.components import Stats
from nqp.core.data import Data

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
        self.assertEqual(1, self.stats.get_value("size"))

    def test_increase(self):
        self.stats.apply_modifier("size", 0.50, 0)
        self.assertEqual(1.5, self.stats.get_value("size"))

    def test_decrease(self):
        self.stats.apply_modifier("size", -0.50, 0)
        self.assertEqual(0.5, self.stats.get_value("size"))

    def test_apply_and_remove(self):
        self.stats.apply_modifier("size", -0.50, 0)
        self.stats.apply_modifier("size", -0.50, 1)
        self.stats.remove_modifier(0)
        self.stats.remove_modifier(1)
        self.assertEqual(1.0, self.stats.get_value("size"))

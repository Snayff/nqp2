import unittest
from unittest.mock import Mock

from pygame import Vector2

from nqp.topography.pathfinding import PriorityQueue
from nqp.topography.terrain import Terrain


class TestPriorityQueue(unittest.TestCase):
    def test_put(self):
        q = PriorityQueue()
        q.put("a", 0)

    def test_get(self):
        q = PriorityQueue()
        q.put("a", 0)
        result = q.get()
        self.assertEqual("a", result)

    def test_get_many(self):
        q = PriorityQueue()
        q.put("c", 2)
        q.put("b", 1)
        q.put("a", 0)
        result = q.get()
        self.assertEqual("a", result)
        result = q.get()
        self.assertEqual("b", result)
        result = q.get()
        self.assertEqual("c", result)

    def test_mixed_operations(self):
        q = PriorityQueue()
        q.put("c", 2)
        q.put("b", 1)
        result = q.get()
        self.assertEqual("b", result)
        result = q.get()
        self.assertEqual("c", result)
        q.put("a", 0)
        result = q.get()
        self.assertEqual("a", result)

    def test_pop_empty(self):
        q = PriorityQueue()
        with self.assertRaises(IndexError):
            q.get()

    def test_pop_empty_many(self):
        q = PriorityQueue()
        q.put("a", 0)
        q.put("a", 0)
        q.get()
        q.get()
        with self.assertRaises(IndexError):
            q.get()

    def test_empty(self):
        q = PriorityQueue()
        self.assertFalse(bool(q))

    def test_not_empty_one_item(self):
        q = PriorityQueue()
        q.put("a", 0)
        self.assertTrue(bool(q))

    def test_not_empty_many(self):
        q = PriorityQueue()
        q.put("a", 0)
        q.put("a", 0)
        self.assertTrue(bool(q))


class TestSearchTerrain(unittest.TestCase):
    def setUp(self):
        self.t = Terrain(Mock(), "biome")

    def test_search_endpoints_px(self):
        # changes to TILE_SIZE will fail this test
        start = Vector2(8, 15)
        end = Vector2(96, 96)
        result = self.t.pathfind_px(start, end)
        self.assertEqual((8, 24), tuple(result[0]))
        self.assertEqual((104, 104), tuple(result[-1]))

    def test_search_path_px(self):
        # changes to TILE_SIZE will fail this test
        # Changes to pathfinding may cause test to fail even if path is valid
        start = Vector2(0, 0)
        end = Vector2(100, 100)
        result = self.t.pathfind_px(start, end)
        result = list(map(tuple, result))
        expected = [
            (8.0, 24.0),
            (8.0, 40.0),
            (8.0, 56.0),
            (8.0, 72.0),
            (8.0, 88.0),
            (8.0, 104.0),
            (24.0, 104.0),
            (40.0, 104.0),
            (56.0, 104.0),
            (72.0, 104.0),
            (88.0, 104.0),
            (104.0, 104.0),
        ]
        self.assertEqual(expected, result)

    def test_search_endpoints(self):
        start = (0, 0)
        end = (6, 6)
        result = self.t.pathfind(start, end)
        self.assertEqual((0, 1), result[0])
        self.assertEqual((6, 6), result[-1])

    def test_search_path(self):
        # Changes to pathfinding may cause test to fail even if path is valid
        start = (0, 0)
        end = (6, 6)
        result = self.t.pathfind(start, end)
        expected = [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (1, 6),
            (2, 6),
            (3, 6),
            (4, 6),
            (5, 6),
            (6, 6),
        ]
        self.assertEqual(expected, result)

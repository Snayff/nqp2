import unittest

import pygame

from nqp.world_elements.camera import Camera


class TestCamera(unittest.TestCase):
    def test_centre(self):
        c = Camera((100, 100))
        c.centre((50, 50))
        self.assertEqual((50, 50), c.get_centre())

    def test_default_pos(self):
        c = Camera((100, 100))
        self.assertEqual((0, 0), c.get_centre())

    def test_zoom_out_size(self):
        c = Camera((100, 100))
        c.zoom = .5
        self.assertEqual((150, 150), c.get_size())

    def test_zoom_in_size(self):
        c = Camera((100, 100))
        c.zoom = -.5
        self.assertEqual((50, 50), c.get_size())

    def test_offset_no_zoom(self):
        c = Camera((100, 100))
        self.assertEqual((50, 50), c.render_offset())

    def test_offset_zoom_out(self):
        c = Camera((100, 100))
        c.zoom = .5
        self.assertEqual((75, 75), c.render_offset())

    def test_offset_zoom_in(self):
        c = Camera((100, 100))
        c.zoom = -.5
        self.assertEqual((25, 25), c.render_offset())

    def test_bound_no_zoom(self):
        c = Camera((100, 100))
        result = c.get_rect()
        self.assertIsInstance(result, pygame.Rect)
        x, y, h, w = result
        self.assertEqual(-50, x)
        self.assertEqual(-50, y)
        self.assertEqual(100, w)
        self.assertEqual(100, h)

    def test_bounds_zoom_out(self):
        c = Camera((100, 100))
        c.zoom = .5
        x, y, w, h = c.get_rect()
        self.assertEqual(-75, x)
        self.assertEqual(-75, y)
        self.assertEqual(150, w)
        self.assertEqual(150, h)

    def test_bounds_zoom_in(self):
        c = Camera((100, 100))
        c.zoom = -.5
        x, y, w, h = c.get_rect()
        self.assertEqual(-25, x)
        self.assertEqual(-25, y)
        self.assertEqual(50, w)
        self.assertEqual(50, h)

    def test_clamp_fitted(self):
        c = Camera((100, 100))
        c.clamp(pygame.Rect(0, 0, 100, 100))
        x, y, w, h = c.get_rect()
        self.assertEqual(0, x)
        self.assertEqual(0, y)
        self.assertEqual(100, w)
        self.assertEqual(100, h)

    def test_clamp_larger_than_bounds(self):
        c = Camera((1000, 1000))
        c.clamp(pygame.Rect(0, 0, 100, 100))
        x, y, w, h = c.get_rect()
        self.assertEqual(0, -450)
        self.assertEqual(0, -450)
        self.assertEqual(1000, w)
        self.assertEqual(1000, h)

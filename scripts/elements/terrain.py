import pygame

from .tile import Tile

TILE_SIZE = 20


class Terrain:
    def __init__(self):
        self.terrain = {}
        self.tile_size = TILE_SIZE
        self.size = (12, 12)
        self.pixel_size = (self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)

    def generate(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                loc = (x, y)
                self.terrain[loc] = Tile("plains", loc)

    def render(self, surf, offset=(0, 0)):
        for loc in self.terrain:
            tile = self.terrain[loc]

            # rendering rects temporarily
            r = pygame.Rect(
                offset[0] + tile.loc[0] * self.tile_size,
                offset[1] + tile.loc[1] * self.tile_size,
                self.tile_size,
                self.tile_size,
            )
            pygame.draw.rect(surf, (200, 200, 200), r, 1)

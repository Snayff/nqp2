import pygame

from .tile import Tile

TILE_SIZE = 20

class Terrain:
    def __init__(self):
        self.terrain = {}
        self.tile_size = TILE_SIZE

    def generate(self):
        for y in range(12):
            for x in range(12):
                loc = (x, y)
                self.terrain[loc] = Tile('plains', loc)

    def render(self, surf, offset=(0, 0)):
        for loc in self.terrain:
            tile = self.terrain[loc]

            # rendering rects temporarily
            r = pygame.Rect(offset[0] + tile.loc[0] * self.tile_size, offset[1] + tile.loc[1] * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.rect(surf, (255, 255, 255), r, 1)

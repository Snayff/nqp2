import pygame

from .tile import Tile

TILE_SIZE = 16


class Terrain:
    def __init__(self, game):
        self.game = game
        self.terrain = {}
        self.tile_size = TILE_SIZE
        self.size = (20, 20)
        self.pixel_size = (self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)

    def generate(self, map_data):
        for y, row in enumerate(map_data):
            for x, tiles in enumerate(row):
                loc = (x, y)
                self.terrain[loc] = [Tile(tile_type, loc) for tile_type in tiles]

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        for loc in self.terrain:
            for tile in self.terrain[loc]:
                tile.render(self.game, surface, self.game.combat.camera.pos)

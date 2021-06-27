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

    def px_to_loc(self, pos):
        loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        return loc

    def check_tile_solid(self, pos):
        loc = self.px_to_loc(pos)
        if loc in self.terrain:
            for tile in self.terrain[loc]:
                if tile.config["solid"]:
                    return True

        return False

    def tile_rect(self, loc):
        if loc in self.terrain:
            return pygame.Rect(loc[0] * self.tile_size, loc[1] * self.tile_size, self.tile_size, self.tile_size)
        return None

    def tile_rect_px(self, pos):
        loc = self.px_to_loc(pos)
        return self.tile_rect(loc)

    def generate(self, map_data):
        for y, row in enumerate(map_data):
            for x, tiles in enumerate(row):
                loc = (x, y)
                self.terrain[loc] = [Tile(tile_type, loc, self.game.data.tiles) for tile_type in tiles]

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        for loc in self.terrain:
            for tile in self.terrain[loc]:
                tile.render(self.game, surface, self.game.combat.camera.pos)

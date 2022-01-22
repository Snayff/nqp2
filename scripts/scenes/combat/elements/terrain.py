import random

import pygame

from . import map_generator, traps
from .pathfinder import Pathfinder
from .tile import Tile

TILE_SIZE = 16
BARRIER_SIZE = 10


def grid_walk(start, end):
    start = list(start)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    nx = abs(dx)
    ny = abs(dy)
    sign_x = 1 if dx > 0 else -1
    sign_y = 1 if dy > 0 else -1

    points = []

    ix = iy = 0
    points.append((start[0], start[1]))
    while (ix < nx) or (iy < ny):
        if nx == 0:
            iy += 1
            start[1] += sign_y
            continue
        if ny == 0:
            ix += 1
            start[0] += sign_x
            continue
        if (0.5 + ix) / nx < (0.5 + iy) / ny:
            ix += 1
            start[0] += sign_x
        else:
            iy += 1
            start[1] += sign_y
        points.append((start[0], start[1]))

    return points


class Terrain:
    def __init__(self, game):
        self._game = game
        self.terrain = {}
        self.tile_size = TILE_SIZE
        self.barrier_size = BARRIER_SIZE
        self.size = (20, 20)
        self.pixel_size = (self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)
        self.boundaries = pygame.Rect(0, 0, 2, 2)
        self.pathfinder = Pathfinder(self)
        self.traps = []
        self.trap_density = 0.02
        self.trap_types = ["spinning_blades", "spinning_blades", "pit"]

    def debug_map(self, overlay_data=[]):
        return "\n".join(
            [
                "".join(
                    [("=" if v else "%") if (x, y) in overlay_data else ("-" if v else "/") for x, v in enumerate(row)]
                )
                for y, row in enumerate(self.pathfinding_array)
            ]
        )

    def gen_pathfinding_map(self):
        x_coords = [t[0] for t in self.terrain]
        y_coords = [t[1] for t in self.terrain]
        x_tile_boundaries = (min(x_coords), max(x_coords))
        y_tile_boundaries = (min(y_coords), max(y_coords))
        self.tile_boundaries = (x_tile_boundaries, y_tile_boundaries)

        self.pathfinding_array = []
        for i in range(y_tile_boundaries[1] - y_tile_boundaries[0] + 1):
            self.pathfinding_array.append([1] * (x_tile_boundaries[1] - x_tile_boundaries[0] + 1))

        for loc in self.terrain:
            for tile in self.terrain[loc]:
                if tile.config["solid"]:
                    path_loc = self.loc_to_path(loc)
                    self.pathfinding_array[path_loc[1]][path_loc[0]] = 0

        self.pathfinder.set_map(self.pathfinding_array)

    def sight_line(self, start, end):
        start_loc = self.px_to_loc(start)
        end_loc = self.px_to_loc(end)
        points = grid_walk(start_loc, end_loc)
        for p in points:
            if p in self.terrain:
                for tile in self.terrain[p]:
                    if tile.config["sight_block"]:
                        return False
            else:
                return False

        return True

    def loc_to_path(self, loc):
        return (loc[0] - self.tile_boundaries[0][0], loc[1] - self.tile_boundaries[1][0])

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

    def check_tile_hoverable(self, pos):
        loc = self.px_to_loc(pos)
        if loc in self.terrain:
            for tile in self.terrain[loc]:
                if not tile.config["hoverable"]:
                    return False
        else:
            return False

        return True

    def tile_rect(self, loc):
        if loc in self.terrain:
            return pygame.Rect(loc[0] * self.tile_size, loc[1] * self.tile_size, self.tile_size, self.tile_size)
        return None

    def tile_rect_px(self, pos):
        loc = self.px_to_loc(pos)
        return self.tile_rect(loc)

    def generate(self, biome):
        map_generator.generate(self._game, self, biome)
        self.gen_pathfinding_map()

    def update(self, dt):
        for trap in self.traps:
            trap.update(dt)

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        for loc in self.terrain:
            for tile in self.terrain[loc]:
                tile.draw(self._game, surface, self._game.combat.camera.pos)

        for trap in self.traps:
            trap.draw(surface, self._game.combat.camera.render_offset())

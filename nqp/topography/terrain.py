import math
import random
from typing import Callable, Dict, List, Optional, Sequence, Tuple, TYPE_CHECKING

import pygame

from nqp.core.constants import BARRIER_SIZE, TILE_SIZE
from nqp.core.game import Game

from .pathfinder import Pathfinder
from .tile import Tile


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


def random_foliage() -> List[int]:
    """
    Return ids for random tile decorations
    """
    return [random.randint(0, 1), random.randint(2, 13)]


class Terrain:
    """
    Draw and manage tiles

    """

    def __init__(self, game: Game, biome: str):
        self._game = game
        self._biome = biome
        self.tiles: Dict[Tuple[int, int], List[Tile]] = {}
        self.size = (20, 20)
        self.pixel_size = (self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)
        self.tile_boundaries = [[], []]
        self.pathfinding_array = list()
        self.boundaries = pygame.Rect(0, 0, 2, 2)
        self.pathfinder = Pathfinder(self)
        self.traps = []
        self.trap_density = 0.02
        self.trap_types = ["spinning_blades", "spinning_blades", "pit"]
        # used when traversing rooms
        self.ignore_boundaries = False

    def debug_map(self, overlay_data: Optional[List] = None):
        if overlay_data is None:
            overlay_data = list()

        return "\n".join(
            [
                "".join(
                    [("=" if v else "%") if (x, y) in overlay_data else ("-" if v else "/") for x, v in enumerate(row)]
                )
                for y, row in enumerate(self.pathfinding_array)
            ]
        )

    def gen_pathfinding_map(self):
        x_coords = [t[0] for t in self.tiles]
        y_coords = [t[1] for t in self.tiles]
        x_tile_boundaries = (min(x_coords), max(x_coords))
        y_tile_boundaries = (min(y_coords), max(y_coords))
        self.tile_boundaries = (x_tile_boundaries, y_tile_boundaries)

        self.pathfinding_array = []
        for i in range(y_tile_boundaries[1] - y_tile_boundaries[0] + 1):
            self.pathfinding_array.append([1] * (x_tile_boundaries[1] - x_tile_boundaries[0] + 1))

        for loc in self.tiles:
            for tile in self.tiles[loc]:
                if tile.config["solid"]:
                    path_loc = self.loc_to_path(loc)
                    self.pathfinding_array[path_loc[1]][path_loc[0]] = 0

        self.pathfinder.set_map(self.pathfinding_array)

    def sight_line(self, start, end):
        start_loc = self.px_to_loc(start)
        end_loc = self.px_to_loc(end)
        points = grid_walk(start_loc, end_loc)
        for p in points:
            if p in self.tiles:
                for tile in self.tiles[p]:
                    if tile.config["sight_block"]:
                        return False
            else:
                return False

        return True

    def loc_to_path(self, loc):
        return (
            loc[0] - self.tile_boundaries[0][0],
            loc[1] - self.tile_boundaries[1][0],
        )

    def px_to_loc(self, pos) -> Tuple[int, int]:
        loc = (int(pos[0] // TILE_SIZE), int(pos[1] // TILE_SIZE))
        return loc

    def check_tile_solid(self, pos):
        loc = self.px_to_loc(pos)

        try:
            tiles = self.tiles[loc]
        except KeyError:
            return self.ignore_boundaries
        else:
            for tile in tiles:
                if tile.config["solid"]:
                    return True

        return self.ignore_boundaries

    def check_tile_hoverable(self, pos):
        loc = self.px_to_loc(pos)
        if loc in self.tiles:
            for tile in self.tiles[loc]:
                if not tile.config["hoverable"]:
                    return False
        else:
            return False

        return True

    def tile_rect(self, loc):
        return pygame.Rect(loc[0] * TILE_SIZE, loc[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def tile_rect_px(self, pos):
        loc = self.px_to_loc(pos)
        return self.tile_rect(loc)

    def generate(self):
        generate(self._game, self, self._biome)
        self.gen_pathfinding_map()

    def update(self, dt):
        for trap in self.traps:
            trap.update(dt)

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2):

        for loc in self.tiles:
            tile_offset = (
                loc[0] * TILE_SIZE + offset[0],
                loc[1] * TILE_SIZE + offset[1],
            )
            for tile in self.tiles[loc]:
                tile.draw(self._game, surface, tile_offset)

        for trap in self.traps:
            trap.draw(surface, offset)


def generate(game: Game, terrain: Terrain, biome: str):
    screen_size = game.window.base_resolution.copy()
    combat_area_size = [int(screen_size[0] // TILE_SIZE), int(screen_size[1] // TILE_SIZE)]
    placement_width = math.ceil(combat_area_size[0] / 4)
    tree_bases = []
    for x in range(combat_area_size[0] + BARRIER_SIZE * 2):
        for y in range(combat_area_size[1] + BARRIER_SIZE * 2):
            loc = (x - BARRIER_SIZE - 1, y - BARRIER_SIZE - 1)
            terrain.tiles[loc] = [Tile([biome, 0, 1], game.data.tiles)]
            if (BARRIER_SIZE < x <= (combat_area_size[0] + BARRIER_SIZE)) and (
                BARRIER_SIZE < y <= (combat_area_size[1] + BARRIER_SIZE)
            ):
                if random.random() < 0.3:
                    terrain.tiles[loc].append(Tile([biome, *random_foliage()], game.data.tiles))
                if random.random() < 0.025:
                    tree_bases.append(loc)
                # place traps
                # elif random.random() < terrain.trap_density:
                #     trap_type = random.choice(terrain.trap_types)
                #     terrain.traps.append(
                #         traps.trap_types[trap_type](game, (loc[0] * TILE_SIZE, loc[1] * TILE_SIZE))
                #     )
            else:
                # place trees around border
                terrain.tiles[loc].append(Tile(["trees", 0, 1], game.data.tiles))

    # place trees randomly
    # for base in tree_bases:
    #     gen_blob(
    #         base,
    #         random.randint(3, 24),
    #         ["trees", 0, 1],
    #         terrain,
    #         floor_filter=lambda x: (not x.config["solid"])
    #         and (x.group != "trees")
    #         and (placement_width < x.loc[0] < combat_area_size[0] - placement_width),
    #     )

    for x in range(combat_area_size[0]):
        loc = (x, int(combat_area_size[1] // 2))
        if loc in terrain.tiles:
            loc_copy = terrain.tiles[loc].copy()
            for tile in loc_copy:
                if tile.config["solid"]:
                    terrain.tiles[loc].remove(tile)

    terrain.boundaries.x = -BARRIER_SIZE * TILE_SIZE
    terrain.boundaries.y = -BARRIER_SIZE * TILE_SIZE
    terrain.boundaries.width = (BARRIER_SIZE * 2 + combat_area_size[0]) * TILE_SIZE
    terrain.boundaries.height = (BARRIER_SIZE * 2 + combat_area_size[1]) * TILE_SIZE


def gen_blob(
    start_pos: Sequence[int],
    count: int,
    tile_type: str,
    terrain: Terrain,
    floor_filter: Optional[Callable] = None,
):
    blob_points = [tuple(start_pos)]
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    for i in range(count):
        placed = False
        while not placed:
            base = random.choice(blob_points)
            direction = random.choice(directions)
            new_pos = (base[0] + direction[0], base[1] + direction[1])
            if new_pos not in blob_points:
                blob_points.append(new_pos)
                placed = True

    for point in blob_points:
        if point in terrain.tiles:
            if floor_filter:
                valid = True
                for base_tile in terrain.tiles[point]:
                    if not floor_filter(base_tile):
                        valid = False
                if not valid:
                    continue

            # terrain.tiles[point].append(Tile(tile_type, point, terrain._game.data.tiles))
            terrain.tiles[point].append(Tile(tile_type, terrain._game.data.tiles))

import random
from itertools import product
from typing import Dict, Iterator, List, Set

import pygame

from nqp.core.constants import BARRIER_SIZE, TILE_SIZE
from nqp.core.definitions import TileLocation
from nqp.core.game import Game
from nqp.topography.pathfinding import search_terrain
from nqp.topography.tile import Tile


def grid_walk(start: TileLocation, end: TileLocation) -> List[TileLocation]:
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
        self.tiles: Dict[TileLocation, List[Tile]] = {}
        self.size: pygame.Vector2 = pygame.Vector2(40 + BARRIER_SIZE * 2, 22 + BARRIER_SIZE * 2)
        self.boundaries: pygame.Rect = pygame.Rect(0, 0, 2, 2)
        self.traps = []
        self.trap_density = 0.02
        self.trap_types = ["spinning_blades", "spinning_blades", "pit"]
        # used when traversing rooms
        self.ignore_boundaries = False
        self.walls: Set[Tile] = set()

    def update_static_pathfinding_data(self):
        """
        Update pathfinding for static level geometry

        """
        self.walls = set()

        for loc in self.tiles:
            for tile in self.tiles[loc]:
                if tile.config["solid"]:
                    self.walls.add(loc)

    def sight_line(self, start: pygame.Vector2, end: pygame.Vector2) -> bool:
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

    def px_to_loc(self, pos: pygame.Vector2) -> TileLocation:
        return int(pos.x // TILE_SIZE), int(pos.y // TILE_SIZE)

    def loc_to_px(self, loc: TileLocation) -> pygame.Vector2:
        return pygame.Vector2(loc) * TILE_SIZE

    def check_tile_inside(self, loc: TileLocation) -> bool:
        return (
            BARRIER_SIZE <= loc[0] < self.size.x - BARRIER_SIZE and BARRIER_SIZE <= loc[1] < self.size.y - BARRIER_SIZE
        )

    def check_tile_solid(self, pos: pygame.Vector2) -> bool:
        if self.ignore_boundaries:
            return False

        loc = self.px_to_loc(pos)
        return loc in self.walls

    def check_tile_hoverable(self, pos: pygame.Vector2) -> bool:
        loc = self.px_to_loc(pos)
        if loc in self.tiles:
            for tile in self.tiles[loc]:
                if not tile.config["hoverable"]:
                    return False
        else:
            return False

        return True

    def tile_rect(self, loc: TileLocation) -> pygame.Rect:
        return pygame.Rect(loc[0] * TILE_SIZE, loc[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def tile_rect_px(self, pos: pygame.Vector2) -> pygame.Rect:
        loc = self.px_to_loc(pos)
        return self.tile_rect(loc)

    def playfield_rect(self) -> pygame.rect:
        """
        Return Rect of the inner part of the Terrain in tile units

        """
        return pygame.Rect(
            BARRIER_SIZE,
            BARRIER_SIZE,
            self.size.x - BARRIER_SIZE * 2,
            self.size.y - BARRIER_SIZE * 2,
        )

    def playfield_rect_px(self) -> pygame.rect:
        """
        Return Rect of the inner part of the Terrain in map units

        """
        return pygame.Rect(
            BARRIER_SIZE * TILE_SIZE,
            BARRIER_SIZE * TILE_SIZE,
            (self.size.x - BARRIER_SIZE * 2) * TILE_SIZE,
            (self.size.y - BARRIER_SIZE * 2) * TILE_SIZE,
        )

    def generate(self):
        self._generate(self._game, self._biome)
        self.update_static_pathfinding_data()

    def update(self, dt: float):
        for trap in self.traps:
            trap.update(dt)

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2):
        for loc, tiles in self.tiles.items():
            screen_pos = (
                loc[0] * TILE_SIZE + offset[0],
                loc[1] * TILE_SIZE + offset[1],
            )
            for tile in tiles:
                tile.draw(self._game, surface, screen_pos)

        for trap in self.traps:
            trap.draw(surface, offset)

    def pathfind(self, start: TileLocation, end: TileLocation) -> List[TileLocation]:
        """
        Pathfind between tile coordinates

        """
        return search_terrain(self, start, end)

    def pathfind_px(self, start: pygame.Vector2, end: pygame.Vector2) -> List[pygame.Vector2]:
        """
        Pathfind between map coordinates ("pixel coordinates")

        """
        offset = pygame.Vector2(TILE_SIZE) / 2
        path_px = []
        for loc in self.pathfind(self.px_to_loc(start), self.px_to_loc(end)):
            path_px.append(self.loc_to_px(loc) + offset)
        return path_px

    def cost(self, start: TileLocation, end: TileLocation):
        """
        Return cost to travel from one tile to the next

        Used for slow tiles like mud, snow, etc

        """
        # TODO: tile movement costs
        return 0

    def in_bounds(self, loc: TileLocation) -> bool:
        return 0 <= loc[0] < self.size.x and 0 <= loc[1] < self.size.y

    def passable(self, loc: TileLocation):
        return True
        # return loc not in self.walls

    def get_exits(self, loc: TileLocation) -> Iterator[TileLocation]:
        """
        Return possible movements from tile location

        """
        (x, y) = loc
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]  # E W N S
        if (x + y) % 2 == 0:
            neighbors.reverse()  # S N W E
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

    def _generate(self, game: Game, biome: str):
        tree_bases = []
        self.tiles = dict()
        for loc in product(range(int(self.size.x)), range(int(self.size.y))):
            self.tiles[loc] = [Tile([biome, 0, 1], game.data.tiles)]
            if self.check_tile_inside(loc):
                if random.random() < 0.3:
                    self.tiles[loc].append(Tile([biome, *random_foliage()], game.data.tiles))
                if random.random() < 0.025:
                    tree_bases.append(loc)
                # place traps
                # elif random.random() < self.trap_density:
                #     trap_type = random.choice(self.trap_types)
                #     self.traps.append(
                #         traps.trap_types[trap_type](game, (loc[0] * TILE_SIZE, loc[1] * TILE_SIZE))
                #     )
            else:
                # place things in the border ("BARRIER")
                tile = Tile(["trees", 0, 1], game.data.tiles)
                assert tile.config["solid"]
                self.tiles[loc].append(tile)

        # place trees randomly
        # for base in tree_bases:
        #     gen_blob(
        #         base,
        #         random.randint(3, 24),
        #         ["trees", 0, 1],
        #         self.
        #         floor_filter=lambda x: (not x.config["solid"])
        #         and (x.group != "trees")
        #         and (placement_width < x.loc[0] < combat_area_size[0] - placement_width),
        #     )

        self.boundaries.x = 0
        self.boundaries.y = 0
        self.boundaries.width = self.size.x * TILE_SIZE
        self.boundaries.height = self.size.y * TILE_SIZE

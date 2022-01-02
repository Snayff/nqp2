import math
import random

from . import traps
from .tile import Tile


def gen_blob(start_pos, count, tile_type, terrain, floor_filter=None):
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
        if point in terrain.terrain:
            if floor_filter:
                valid = True
                for base_tile in terrain.terrain[point]:
                    if not floor_filter(base_tile):
                        valid = False
                if not valid:
                    continue

            terrain.terrain[point].append(Tile(tile_type, point, terrain.game.data.tiles))


def random_foliage():
    """
    Return ids for random tile decorations
    """
    return [random.randint(0, 1), random.randint(2, 13)]


def generate(game, terrain, biome):
    screen_size = game.window.base_resolution.copy()
    combat_area_size = [int(screen_size[0] // terrain.tile_size), int(screen_size[1] // terrain.tile_size)]
    placement_width = math.ceil(combat_area_size[0] / 4)
    tree_bases = []
    for x in range(combat_area_size[0] + terrain.barrier_size * 2):
        for y in range(combat_area_size[1] + terrain.barrier_size * 2):
            loc = (x - terrain.barrier_size - 1, y - terrain.barrier_size - 1)
            terrain.terrain[loc] = [Tile([biome, 0, 1], loc, game.data.tiles)]
            if (terrain.barrier_size < x <= (combat_area_size[0] + terrain.barrier_size)) and (
                terrain.barrier_size < y <= (combat_area_size[1] + terrain.barrier_size)
            ):
                if random.random() < 0.3:
                    terrain.terrain[loc].append(Tile([biome, *random_foliage()], loc, game.data.tiles))
                if random.random() < 0.025:
                    tree_bases.append(loc)
                # place traps
                # elif random.random() < terrain.trap_density:
                #     trap_type = random.choice(terrain.trap_types)
                #     terrain.traps.append(
                #         traps.trap_types[trap_type](game, (loc[0] * terrain.tile_size, loc[1] * terrain.tile_size))
                #     )
            else:
                # place trees around border
                terrain.terrain[loc].append(Tile(["trees", 0, 1], loc, game.data.tiles))

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
        if loc in terrain.terrain:
            loc_copy = terrain.terrain[loc].copy()
            for tile in loc_copy:
                if tile.config["solid"]:
                    terrain.terrain[loc].remove(tile)

    terrain.boundaries.x = -terrain.barrier_size * terrain.tile_size
    terrain.boundaries.y = -terrain.barrier_size * terrain.tile_size
    terrain.boundaries.width = (terrain.barrier_size * 2 + combat_area_size[0]) * terrain.tile_size
    terrain.boundaries.height = (terrain.barrier_size * 2 + combat_area_size[1]) * terrain.tile_size

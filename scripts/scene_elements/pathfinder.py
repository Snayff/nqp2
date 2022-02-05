import tcod


class Pathfinder:
    def __init__(self, terrain):
        self.tcod_map = None
        self.terrain = terrain

    def set_map(self, map_data):
        import numpy as np

        m = np.asarray(map_data, dtype=np.dtype(np.int16))
        self.tcod_map = tcod.path.AStar(m, diagonal=0)

    def route(self, start, end):
        if self.tcod_map:
            tcod_path = self.tcod_map.get_path(start[1], start[0], end[1], end[0])
            return [
                (point[1] + self.terrain.tile_boundaries[0][0], point[0] + self.terrain.tile_boundaries[1][0])
                for point in tcod_path
            ]

        return []

    def px_route(self, start, end):
        start = (
            int(start[0] // self.terrain.tile_size) - self.terrain.tile_boundaries[0][0],
            int(start[1] // self.terrain.tile_size) - self.terrain.tile_boundaries[1][0],
        )
        end = (
            int(end[0] // self.terrain.tile_size) - self.terrain.tile_boundaries[0][0],
            int(end[1] // self.terrain.tile_size) - self.terrain.tile_boundaries[1][0],
        )
        tcod_path = self.route(start, end)
        return [
            (
                point[0] * self.terrain.tile_size + self.terrain.tile_size // 2,
                point[1] * self.terrain.tile_size + self.terrain.tile_size // 2,
            )
            for point in tcod_path
        ]

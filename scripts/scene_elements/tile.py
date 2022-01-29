from copy import deepcopy


class Tile:
    """
    Single Tile as part of a Terrain

    """

    def __init__(self, tile_type, tile_config):
        self.type = tile_type
        self.config = deepcopy(tile_config[("default", 0, 0)])
        if tuple(self.type) in tile_config:
            self.config.update(tile_config[tuple(self.type)])

    @property
    def group(self):
        return self.type[0]

    @property
    def src_y(self):
        return self.type[1]

    @property
    def src_x(self):
        return self.type[2]

    def draw(self, game, surf, dest):
        tileset = game.assets.tilesets[self.group]
        if self.group[-8:] == "animated":
            self.type[2] = int((game.master_clock * 2) % len(tileset[self.src_y]))
        img = tileset[self.src_y][self.src_x]
        surf.blit(img, dest)

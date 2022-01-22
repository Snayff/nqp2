from copy import deepcopy


class Tile:
    def __init__(self, tile_type, location, tile_config):
        self.type = tile_type
        self.loc = list(location)

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

    def draw(self, game, surf, offset=[0, 0]):
        tileset = game.assets.tilesets[self.group]
        if self.group[-8:] == "animated":
            self.type[2] = int((game.master_clock * 2) % len(tileset[self.src_y]))

        img = tileset[self.src_y][self.src_x]

        tile_size = game.world.ui.terrain.tile_size

        surf.blit(img, (self.loc[0] * tile_size - offset[0], self.loc[1] * tile_size - offset[1]))

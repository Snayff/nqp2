from elements.terrain import Terrain

"""
This is the object that manages the entire combat scene.
"""
class Combat:
    def __init__(self, game):
        self.game = game
        self.terrain = Terrain()
        self.terrain.generate()

    def update(self):
        pass

    def render(self):
        self.terrain.render(self.game.window.display, (100, 50))

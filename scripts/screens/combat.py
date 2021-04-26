from scripts.constants import CombatState
from scripts.elements.terrain import Terrain
from scripts.ui.combat import CombatUI

"""
This is the object that manages the entire combat scene.
"""
class Combat:
    def __init__(self, game):
        self.game = game

        self.terrain = Terrain()
        self.terrain.generate()

        self.ui = CombatUI(game)

        self.deck = self.game.memory.deck.copy()
        self.hand = self.deck.draw(5)

        self.state = CombatState.CHOOSE_CARD

    def update(self):
        self.ui.update()

    def render(self):
        self.terrain.render(self.game.window.display, (100, 50))
        self.ui.render(self.game.window.display)

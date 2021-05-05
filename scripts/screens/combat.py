from scripts.constants import CombatState
from scripts.elements.camera import Camera
from scripts.elements.terrain import Terrain
from scripts.elements.unit_manager import UnitManager
from scripts.ui.combat import CombatUI

"""
This is the object that manages the entire combat scene.
"""
class Combat:
    def __init__(self, game):
        self.game = game

        self.camera = Camera()
        self.camera.pos = [-100, -50]

        self.terrain = Terrain()
        self.terrain.generate()

        self.units = UnitManager(game)

        self.ui = CombatUI(game)

        self.deck = self.game.memory.deck.copy()
        self.hand = self.deck.draw(5)

        self.state = CombatState.CHOOSE_CARD

    def update(self):
        self.ui.update()
        self.units.update()

        # temporary hack to end watch phase
        if self.game.combat.state == CombatState.WATCH:
            self.state = CombatState.CHOOSE_CARD

    def render(self):
        self.terrain.render(self.game.window.display, self.camera.render_offset())
        self.units.render(self.game.window.display, self.camera.render_offset())
        self.ui.render(self.game.window.display)

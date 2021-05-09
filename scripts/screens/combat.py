from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.elements.camera import Camera
from scripts.elements.card_collection import CardCollection
from scripts.elements.terrain import Terrain
from scripts.elements.unit_manager import UnitManager
from scripts.misc.constants import CombatState
from scripts.ui.combat import CombatUI

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Combat"]


class Combat:
    """
    Handles Combat interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.camera: Camera = Camera()
        self.camera.pos = [-100, -50]

        self.terrain: Terrain = Terrain()
        self.terrain.generate()

        self.units: UnitManager = UnitManager(game)

        self.ui: CombatUI = CombatUI(game)

        self.deck: CardCollection = self.game.memory.deck.copy()
        self.hand = self.deck.draw(5)

        self.state: CombatState = CombatState.CHOOSE_CARD

    def update(self):
        self.ui.update()
        self.units.update()

        # temporary hack to end watch phase
        if self.game.combat.state == CombatState.WATCH:
            self.state = CombatState.CHOOSE_CARD

        # end combat when all cards spent
        if len(self.hand.cards) == 0:
            self.game.active_screen = self.game.overworld

    def render(self):
        self.terrain.render(self.game.window.display, self.camera.render_offset())
        self.units.render(self.game.window.display, self.camera.render_offset())
        self.ui.render(self.game.window.display)

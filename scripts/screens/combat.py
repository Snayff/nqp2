from __future__ import annotations

from scripts.misc.constants import CombatState
from scripts.elements.camera import Camera
from scripts.elements.terrain import Terrain
from scripts.elements.unit_manager import UnitManager
from scripts.ui.combat import CombatUI

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Combat"]


class Combat:
    """
    Represents the combat and handles related interactions.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.camera = Camera()
        self.camera.pos = [-100, -50]

        self.terrain = Terrain()
        self.terrain.generate()

        self.units = UnitManager(game)

        self.ui = CombatUI(game)

        self.deck = self.game.memory.deck.copy()
        self.hand = self.deck.draw(5)

        self.state: CombatState = CombatState.CHOOSE_CARD

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

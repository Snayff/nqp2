from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.elements.camera import Camera
from scripts.elements.card_collection import CardCollection
from scripts.elements.enemy_combatants_generator import EnemyCombatantsGenerator
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

        self.enemy_generator = EnemyCombatantsGenerator(game)

        self.ui: CombatUI = CombatUI(game)

        self.deck: CardCollection = self.game.memory.deck.copy()
        self.hand = self.deck.draw(5)

        self.state: CombatState = CombatState.CHOOSE_CARD

        self.combat_speed = 1

        self.all_entities = self.get_all_entities()

    def begin_combat(self):
        self.enemy_generator.generate()

    def get_all_entities(self):
        entities = []
        for unit in self.units.units:
            entities += unit.entities
        return entities

    def update(self):
        self.dt = self.combat_speed * self.game.window.dt

        # call once per frame instead of once per entity to save processing power
        self.all_entities = self.get_all_entities()

        self.ui.update()
        self.units.update()

        # reduce combat speed when applicable
        if self.game.combat.state == CombatState.WATCH:
            self.combat_speed = 1
        else:
            self.combat_speed = 0.3

        # end combat when all cards spent
        # if len(self.hand.cards) == 0:
        #    self.game.active_screen = self.game.overworld

    def render(self):
        self.terrain.render(self.game.window.display, self.camera.render_offset())
        self.units.render(self.game.window.display, self.camera.render_offset())
        self.ui.render(self.game.window.display)

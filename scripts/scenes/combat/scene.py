from __future__ import annotations

import logging
import time
from typing import List, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import CombatState, SceneType
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.card_collection import CardCollection
from scripts.scenes.combat.elements.enemy_combatants_generator import EnemyCombatantsGenerator
from scripts.scenes.combat.elements.terrain import Terrain
from scripts.scenes.combat.elements.unit_manager import UnitManager
from scripts.scenes.combat.ui import CombatUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["CombatScene"]


class CombatScene(Scene):
    """
    Handles CombatScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.camera: Camera = Camera()
        self.camera.pos = [-100, -50]

        self.terrain: Terrain = Terrain()
        self.terrain.generate()

        self.units: UnitManager = UnitManager(game)

        self.enemy_generator = EnemyCombatantsGenerator(game)

        self.ui: CombatUI = CombatUI(game)

        self.units_to_place: List[int] = []  # unit ids

        # FIXME - why are we taking a copy rather than referencing the unit deck in memory?
        self.deck: CardCollection = self.game.memory.unit_deck.copy()
        self.hand = self.deck.draw(5)

        self.state: CombatState = CombatState.UNIT_CHOOSE_CARD

        self.combat_speed = 1
        self.dt = 0

        self.all_entities = self.get_all_entities()

        # record duration
        end_time = time.time()
        logging.info(f"CombatScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def begin_combat(self):
        self.game.combat.refresh_units_to_place()
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

        # end combat when either side is empty
        if self.game.combat.state not in [CombatState.UNIT_CHOOSE_CARD, CombatState.UNIT_SELECT_TARGET]:
            player_entities = [e for e in self.all_entities if e.team == "player"]
            if (len(player_entities) == 0) or (len(player_entities) == len(self.all_entities)):
                self.game.change_scene(SceneType.OVERWORLD)

        self.ui.update()
        self.units.update()

        # run at normal speed during watch phase
        if self.game.combat.state == CombatState.WATCH:
            self.combat_speed = 1

        # pause combat during unit placement
        elif self.game.combat.state in [CombatState.UNIT_CHOOSE_CARD, CombatState.UNIT_SELECT_TARGET]:
            self.combat_speed = 0

        # slow down combat when playing actions
        else:
            self.combat_speed = 0.3

    def render(self):
        self.terrain.render(self.game.window.display, self.camera.render_offset())
        self.units.render(self.game.window.display, self.camera.render_offset())
        self.ui.render(self.game.window.display)

    def refresh_units_to_place(self):
        """
        Refresh the unit ids held in units to place
        """
        for unit in self.game.memory.player_troupe.units.keys():
            self.units_to_place.append(unit)

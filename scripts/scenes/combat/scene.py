from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import CombatState, PostCombatState, SceneType
from scripts.scenes.combat.elements.actions import actions
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.card_collection import CardCollection
from scripts.scenes.combat.elements.enemy_combatants_generator import EnemyCombatantsGenerator
from scripts.scenes.combat.elements.terrain import Terrain
from scripts.scenes.combat.elements.unit_manager import UnitManager
from scripts.scenes.combat.ui import CombatUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["CombatScene"]


########### To Do List #############
# TODO - Convert actions to cooldown based, instead of cards.
# TODO - Injury/healing (health persistence outside of combat. See Design Doc for info.)
# TODO - add combat with multiple participants, not just player vs enemy; team vs team or free for all.
# FIXME - ensure all attributes are created in __init__.


class CombatScene(Scene):
    """
    Handles CombatScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        # record duration
        end_time = time.time()
        logging.info(f"CombatScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)

        self.dt = self.combat_speed * self.game.window.dt

        # call once per frame instead of once per entity to save processing power
        self.all_entities = self.get_all_entities()

        # end combat when either side is empty
        if self.game.combat.state not in [CombatState.UNIT_CHOOSE_CARD, CombatState.UNIT_SELECT_TARGET]:
            player_entities = [e for e in self.all_entities if e.team == "player"]
            if len(player_entities) == 0:
                self.game.post_combat.state = PostCombatState.DEFEAT
                self.game.change_scene(SceneType.POST_COMBAT)

            elif len(player_entities) == len(self.all_entities):
                self.game.post_combat.state = PostCombatState.VICTORY
                self.game.change_scene(SceneType.POST_COMBAT)

        self.ui.update(delta_time)
        self.units.update(delta_time)

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

    def begin_combat(self):
        self.camera: Camera = Camera()
        self.camera.pos = [0, 100]

        self.terrain: Terrain = Terrain(self.game)
        self.terrain.generate(self.game.assets.maps["plains_1"])

        self.units: UnitManager = UnitManager(self.game)

        self.enemy_generator = EnemyCombatantsGenerator(self.game)

        self.ui: CombatUI = CombatUI(self.game)

        self.actions = actions

        self.state: CombatState = CombatState.UNIT_CHOOSE_CARD

        self.combat_speed = 1
        self.dt = 0

        self.all_entities = self.get_all_entities()

        self.enemy_generator.generate()
        self.game.memory.unit_deck.from_troupe(self.game.memory.player_troupe)
        self.deck: CardCollection = self.game.memory.unit_deck.copy()
        self.hand = self.deck.draw(5)

        self.leadership_points_spent = 0  # points spent to place units

    def get_all_entities(self):
        entities = []
        for unit in self.units.units:
            entities += unit.entities
        return entities

    def get_team_center(self, team):
        count = 0
        pos_totals = [0, 0]
        for unit in self.units.units:
            if unit.team == team:
                pos_totals[0] += unit.pos[0]
                pos_totals[1] += unit.pos[1]
                count += 1
        if count:
            return [pos_totals[0] / count, pos_totals[1] / count]
        else:
            return None

    def start_action_phase(self):
        self.deck: CardCollection = self.game.memory.action_deck.copy()
        self.hand = self.deck.draw(5)

    def _get_random_combat(self) -> Dict[str, Any]:
        if len(self.game.data.combats) > 0:
            level = self.game.overworld.level
            combats = self.game.data.combats.values()

            # ensure only combat for this level or lower
            possible_combats = []
            possible_combats_occur_rates = []
            for combat in combats:
                if combat["level_available"] <= level:
                    possible_combats.append(combat)
                    occur_rate = self.game.data.get_combat_occur_rate(combat["id"])
                    possible_combats_occur_rates.append(occur_rate)

            combat_ = self.game.rng.choices(possible_combats, possible_combats_occur_rates)[0]
        else:
            combat_ = {}
        return combat_

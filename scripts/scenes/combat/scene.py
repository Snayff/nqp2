from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, TYPE_CHECKING

import pygame

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import CombatState, PostCombatState, SceneType
from scripts.scenes.combat.elements.actions import actions
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.card_collection import CardCollection
from scripts.scenes.combat.elements.enemy_combatants_generator import EnemyCombatantsGenerator
from scripts.scenes.combat.elements.terrain import Terrain
from scripts.scenes.combat.elements.unit_manager import UnitManager
from scripts.scenes.combat.elements.projectile_manager import ProjectileManager
from scripts.scenes.combat.ui import CombatUI

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["CombatScene"]


########### To Do List #############

# FIXME - ensure all attributes are created in __init__.


class CombatScene(Scene):
    """
    Handles CombatScene interactions and consolidates the rendering.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.COMBAT)

        self.camera: Camera = Camera()
        self.terrain: Terrain = Terrain(self.game)
        self.units: UnitManager = UnitManager(self.game)
        self.projectiles: ProjectileManager = ProjectileManager(self.game)

        self.enemy_generator = EnemyCombatantsGenerator(self.game)

        self.ui: CombatUI = CombatUI(self.game)

        self.actions = actions
        self.skill_cooldowns = []

        self.state: CombatState = CombatState.UNIT_CHOOSE_CARD

        self.combat_speed = 1
        self.force_idle = True
        self.dt = 0
        self.combat_ending_timer = -1

        self.last_unit_death = None

        self.all_entities = None

        self.leadership_points_spent: int = 0  # points spent to place units
        self.combat_category: str = "basic"

        # record duration
        end_time = time.time()
        logging.info(f"CombatScene: initialised in {format(end_time - start_time, '.2f')}s.")

    @property
    def general_state(self):
        if self.state in [CombatState.UNIT_SELECT_TARGET, CombatState.UNIT_CHOOSE_CARD]:
            return 'units'
        else:
            return 'actions'

    def update(self, delta_time: float):
        super().update(delta_time)

        self.dt = self.combat_speed * self.game.window.dt

        if self.combat_ending_timer != -1:
            self.combat_ending_timer += self.game.window.dt
            self.combat_speed = 0.3 - (0.05 * self.combat_ending_timer)
            self.camera.zoom = 1 + (self.combat_ending_timer / 2)
            self.force_idle = True
            self.game.combat.state == CombatState.WATCH
            if self.last_unit_death:
                # average the last positions of the last entity to die and the killer of that entity
                focus_point = ((self.last_unit_death[0].pos[0] + self.last_unit_death[1].pos[0]) / 2, (self.last_unit_death[0].pos[1] + self.last_unit_death[1].pos[1]) / 2)
                # gradually move camera
                self.camera.pos[0] += ((focus_point[0] - self.game.window.display.get_width() // 2) - self.camera.pos[0]) / 10 * (self.game.window.dt * 60)
                self.camera.pos[1] += ((focus_point[1] - self.game.window.display.get_height() // 2) - self.camera.pos[1]) / 10 * (self.game.window.dt * 60)
            if self.combat_ending_timer > 4:
                self.end_combat()
                if self.game.post_combat.state == PostCombatState.DEFEAT:
                    self.game.combat.process_defeat()
                self.game.change_scene(SceneType.POST_COMBAT)

        # reduce skill cooldowns
        for i in range(len(self.skill_cooldowns)):
            self.skill_cooldowns[i] = max(self.skill_cooldowns[i] - self.dt, 0)

        # call once per frame instead of once per entity to save processing power
        self.all_entities = self.get_all_entities()

        # end combat when either side is empty
        if (self.game.combat.state not in [CombatState.UNIT_CHOOSE_CARD, CombatState.UNIT_SELECT_TARGET]) and (self.combat_ending_timer == -1):
            player_entities = [e for e in self.all_entities if e.team == "player"]
            if len(player_entities) == 0:
                self.combat_ending_timer = 0
                self.game.post_combat.state = PostCombatState.DEFEAT
                self.process_defeat()

            elif len(player_entities) == len(self.all_entities):
                self.combat_ending_timer = 0
                self.game.post_combat.state = PostCombatState.VICTORY
                self.process_victory()

        self.ui.update(delta_time)
        self.ui.rebuild_ui()
        self.units.update(delta_time)
        self.projectiles.update(delta_time)

        # run at normal speed during watch phase
        if self.game.combat.state == CombatState.WATCH:
            self.combat_speed = 1
            self.force_idle = False

        # pause combat during unit placement
        elif self.game.combat.state in [CombatState.UNIT_CHOOSE_CARD, CombatState.UNIT_SELECT_TARGET]:
            self.combat_speed = 1
            self.force_idle = True

        # slow down combat when playing actions
        else:
            self.combat_speed = 0.3
            self.force_idle = False

    def render(self):
        combat_surf = pygame.Surface(self.game.window.display.get_size())
        self.terrain.render(combat_surf, self.camera.render_offset())
        self.units.render(combat_surf, self.camera.render_offset())
        self.projectiles.render(combat_surf, self.camera.render_offset())
        if self.camera.zoom != 1:
            combat_surf = pygame.transform.scale(combat_surf, (int(combat_surf.get_width() * self.camera.zoom), int(combat_surf.get_height() * self.camera.zoom)))
        self.game.window.display.blit(combat_surf, (-(combat_surf.get_width() - self.game.window.display.get_width()) // 2, -(combat_surf.get_height() - self.game.window.display.get_height()) // 2))

        self.ui.render(self.game.window.display)

    def reset(self):
        self.camera = Camera()
        self.camera.pos = [0, 0]

        self.combat_speed = 1
        self.dt = 0

        self.state: CombatState = CombatState.UNIT_CHOOSE_CARD

    def generate_combat(self):
        self.terrain: Terrain = Terrain(self.game)
        self.terrain.generate(self.game.assets.maps["plains_1"])

        self.units: UnitManager = UnitManager(self.game)

        self.enemy_generator = EnemyCombatantsGenerator(self.game)

        self.ui: CombatUI = CombatUI(self.game)

        self.actions = actions

        self.all_entities = self.get_all_entities()

        self.enemy_generator.generate()

        self.placeable_units = self.game.memory.player_troupe._unit_ids.copy()
        self.units_are_available = [True] * len(self.placeable_units)
        self.skill_cooldowns = [0] * len(self.game.memory.player_actions)

        self.leadership_points_spent = 0  # points spent to place units

    def end_combat(self):
        # process injuries
        remove_units = []
        for unit in self.game.memory.player_troupe._units.values():
            if unit in self.units.units:
                # do an update to ensure unit.alive is updated
                unit.update(0.0001)

                # add injury for units killed in combat
                if not unit.alive:
                    unit.injuries += 1
                    # remove unit from troupe if the unit took too many injuries
                    if unit.injuries >= 3:
                        remove_units.append(unit.id)
            else:
                # remove injury for units not used in combat
                unit.injuries = max(0, unit.injuries - 1)

        # remove units after since they can't be removed during iteration
        for unit in remove_units:
            self.game.memory.player_troupe.remove_unit(unit)

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
        self.ui.selected_col = 0

    def _get_random_combat(self) -> Dict[str, Any]:
        if len(self.game.data.combats) > 0:
            level = self.game.memory.level
            combats = self.game.data.combats.values()

            # get possible combats
            possible_combats = []
            possible_combats_occur_rates = []
            for combat in combats:
                # ensure only combat for this level or lower and of desired type
                if combat["level_available"] <= level and combat["category"] == self.combat_category:
                    possible_combats.append(combat)
                    occur_rate = self.game.data.get_combat_occur_rate(combat["type"])
                    possible_combats_occur_rates.append(occur_rate)

            combat_ = self.game.rng.choices(possible_combats, possible_combats_occur_rates)[0]
        else:
            combat_ = {}
        return combat_

    def process_defeat(self):
        """
        Remove morale.
        """
        if self.combat_category == "basic":
            morale_removed = -1
        else:
            # self.combat_category == "basic":
            morale_removed = -999

        self.game.memory.amend_morale(morale_removed)

        # TODO - add injury allocation

        # transition to post-combat
        self.game.post_combat.state = PostCombatState.DEFEAT
        self.game.change_scene(SceneType.POST_COMBAT)

    def process_victory(self):
        if self.combat_category == "basic":
            new_state = PostCombatState.VICTORY
        else:
            # self.combat_category == "boss":
            new_state = PostCombatState.BOSS_VICTORY
        self.game.post_combat.state = new_state
        self.game.change_scene(SceneType.POST_COMBAT)

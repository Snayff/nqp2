from __future__ import annotations

import logging
import time
from typing import Any, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType, WorldState
from scripts.scene_elements.particle_manager import ParticleManager
from scripts.scene_elements.projectile_manager import ProjectileManager
from scripts.scene_elements.troupe import Troupe
from scripts.scenes.world.ui import WorldUI

if TYPE_CHECKING:
    from typing import Dict, List

    from scripts.core.game import Game

__all__ = ["WorldScene"]


class WorldScene(Scene):
    """
    Handles WorldScene interactions and consolidates the rendering. Draws the underlying map present in most Scenes.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.WORLD)

        self.ui: WorldUI = WorldUI(game, self)

        self.state: WorldState = WorldState.IDLE
        self.unit_grid: List = []
        self.last_unit_death = None

        # unit selection grid dimensions
        self.grid_size: List[int, int] = [3, 8]  # col, row
        self.grid_cell_size: int = 32
        self.grid_margin: int = 32

        self.projectiles: ProjectileManager = ProjectileManager(self._game)
        self.particles: ParticleManager = ParticleManager()
        self.combat_category: str = "basic"
        self._combat_ending_timer: float = -1
        self.enemy_troupe_id: int = -1

        self._game_log: List[str] = []  # list of str describing what has happened during the game

        # record duration
        end_time = time.time()
        logging.debug(f"WorldScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        # amend delta time by game speed adn cascade down
        mod_delta_time = self._game.memory.game_speed * delta_time

        super().update(mod_delta_time)
        self.ui.update(mod_delta_time)

        # update all troupes
        for troupe in self._game.memory.troupes.values():
            troupe.update(mod_delta_time)

        self.particles.update(mod_delta_time)

        if self.state == WorldState.IDLE:
            self._update_idle_state(mod_delta_time)

        elif self.state == WorldState.COMBAT:
            self._update_combat_state(mod_delta_time)

    def activate(self):
        super().activate()

        self.align_unit_pos_to_unit_grid()

        # force idle
        for troupe in self._game.memory.troupes.values():
            troupe.set_force_idle(True)

    def reset(self):
        self.ui = WorldUI(self._game, self)

        self.state = WorldState.IDLE
        self.unit_grid = []
        self.last_unit_death = None

        # unit selection grid dimensions
        self.grid_size = [3, 8]  # col, row
        self.grid_cell_size = 32
        self.grid_margin = 32

        self.projectiles = ProjectileManager(self._game)
        self.particles = ParticleManager()
        self.combat_category = "basic"
        self._combat_ending_timer = -1
        self.enemy_troupe_id = -1

        self._game_log = []  # list of str describing what has happened during the game

    def align_unit_pos_to_unit_grid(self):
        """
        Add player's units to the unit_grid and align their positions.
        """
        self.unit_grid = []

        units = self._game.memory.player_troupe.units.values()
        for unit in units:
            self.unit_grid.append(unit)

        max_rows = self.grid_size[1]
        grid_margin = self.grid_margin
        grid_cell_size = self.grid_cell_size

        for i, unit in enumerate(self.unit_grid):
            x = i // max_rows
            y = i % max_rows
            unit.set_position([grid_margin + x * grid_cell_size, grid_margin + y * grid_cell_size])

    def move_to_new_room(self):
        """
        Move Units to a new room.
        """
        # TODO - write method

        # TEST assume room is combat
        self.generate_combat()

        # once new room ready but not active
        if self._game.event.roll_for_event():
            self.state = WorldState.IDLE
            self._game.event.load_random_event()
            self._game.activate_scene(SceneType.EVENT)

    def generate_combat(self):
        """
        Generate a random combat
        """
        rng = self._game.rng

        combat = self._get_random_combat()
        logging.debug(f"{combat['type']} combat chosen.")
        num_units = len(combat["units"])

        enemy_troupe = Troupe(self._game, "enemy", [])

        # generate positions
        positions = []
        for i in range(num_units):
            # choose a random spot on the right side of the map
            while True:
                pos = [
                    self._game.window.base_resolution[0] // 4 * 3
                    + rng.random() * (self._game.window.base_resolution[0] // 4),
                    rng.random() * self._game.window.base_resolution[1],
                ]
                if not self.ui.terrain.check_tile_solid(pos):
                    break
            positions.append(pos)

        # generate units
        if self._game.debug.debug_mode:
            ids = enemy_troupe.debug_init_units()
            ids = ids[:num_units]
        else:

            ids = enemy_troupe.generate_specific_units(unit_types=combat["units"])

        # assign positions and add to combat
        for id_ in ids:
            unit = enemy_troupe.units[id_]
            unit.pos = positions.pop(0)

        troupe_id = self._game.memory.add_troupe(enemy_troupe)
        self.enemy_troupe_id = troupe_id

        self._combat_ending_timer = -1

    def _get_random_combat(self) -> Dict[str, Any]:
        if len(self._game.data.combats) > 0:
            level = self._game.memory.level
            combats = self._game.data.combats.values()

            # get possible combats
            possible_combats = []
            possible_combats_occur_rates = []
            for combat in combats:
                # ensure only combat for this level or lower and of desired type
                if combat["level_available"] <= level and combat["category"] == self.combat_category:
                    possible_combats.append(combat)
                    occur_rate = self._game.data.get_combat_occur_rate(combat["type"])
                    possible_combats_occur_rates.append(occur_rate)

            combat_ = self._game.rng.choices(possible_combats, possible_combats_occur_rates)[0]
        else:
            combat_ = {}
        return combat_

    def _update_idle_state(self, delta_time):
        """
        Make updates for the idle state
        """
        pass

    def _update_combat_state(self, delta_time):
        """
        Make updates for the combat state
        """
        self.projectiles.update(delta_time)

        # if combat ending
        if self._combat_ending_timer != -1:
            self._combat_ending_timer += delta_time
            self._game.memory.set_game_speed(0.3 - (0.05 * self._combat_ending_timer))
            self.ui.camera.zoom = 1 + (self._combat_ending_timer / 2)
            for troupe in self._game.memory.troupes.values():
                troupe.set_force_idle(True)

            # TODO - what is last death?
            if self.last_unit_death:
                # average the last positions of the last entity to die and the killer of that entity
                focus_point = (
                    (self.last_unit_death[0].pos[0] + self.last_unit_death[1].pos[0]) / 2,
                    (self.last_unit_death[0].pos[1] + self.last_unit_death[1].pos[1]) / 2,
                )
                # gradually move camera
                self.ui.camera.pos[0] += (
                    ((focus_point[0] - self._game.window.display.get_width() // 2) - self.ui.camera.pos[0])
                    / 10
                    * (self._game.window.delta_time * 60)
                )
                self.ui.camera.pos[1] += (
                    ((focus_point[1] - self._game.window.display.get_height() // 2) - self.ui.camera.pos[1])
                    / 10
                    * (self._game.window.delta_time * 60)
                )

        # end combat when either side is empty
        if (self.state == WorldState.COMBAT) and (self._combat_ending_timer == -1):
            all_entities = self._game.memory.get_all_entities()
            player_entities = [e for e in all_entities if e.team == "player"]
            if len(player_entities) == 0:
                self._process_defeat()

            elif len(player_entities) == len(all_entities):
                self._process_victory()

    def _process_defeat(self):
        """
        Process the defeat, such as removing morale.
        """
        self.combat_ending_timer = 0

        self.state = WorldState.DEFEAT
        self.ui.rebuild_ui()

    def _process_victory(self):
        """
        Process victory,
        """
        self.combat_ending_timer = 0

        self.ui.victory_timer = 0
        self.state = WorldState.COMBAT_VICTORY
        self.ui.rebuild_ui()

    def end_combat(self):
        """
        End the combat
        """
        self._game.memory.set_game_speed(1)
        for troupe in self._game.memory.troupes.values():
            troupe.set_force_idle(True)

        self._process_new_injuries()

    def _process_new_injuries(self):
        """
        Process new injuries and resulting deaths
        """
        remove_units = []
        combat_end_data = []
        for i, unit in enumerate(self._game.memory.player_troupe.units.values()):

            # do an update to ensure unit.alive is updated
            unit.update(0.0001)

            # add injury for units killed in combat
            if not unit.alive:
                unit.injuries += 1
                # remove unit from troupe if the unit took too many injuries
                if unit.injuries >= self._game.data.config["unit_properties"]["injuries_before_death"]:
                    remove_units.append(unit.id)
                    combat_end_data.append(f"{unit.type} died due to their injuries.")
                else:
                    combat_end_data.append(f"{unit.type} was injured in battle.")

        # remove units after since they can't be removed during iteration
        for unit in remove_units:
            self._game.memory.player_troupe.remove_unit(unit)

        self._game_log.extend(combat_end_data)

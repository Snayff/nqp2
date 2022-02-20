from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import WorldState
from scripts.core.debug import Timer
from scripts.scene_elements.troupe import Troupe

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene


__all__ = ["CombatController"]


class CombatController(Controller):
    """
    Combat game functionality and combat only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("CombatController initialised"):
            super().__init__(game, parent_scene)
            self.victory_duration: float = 0.0
            self._combat_ending_timer: float = -1
            self.last_unit_death: List = list()

            # state
            self.combat_category: str = "basic"
            self.enemy_troupe_id: int = -1

            self._game_log: List[str] = []  # TODO - needs moving to model

    def update(self, delta_time: float):
        # if combat ending
        if self._combat_ending_timer != -1:
            self._combat_ending_timer += delta_time
            self._game.memory.set_game_speed(0.3 - (0.05 * self._combat_ending_timer))
            # self.ui.camera.zoom = 1 + (self._combat_ending_timer / 2)

            for troupe in self._game.memory.troupes.values():
                troupe.set_force_idle(True)

        # end combat when either side is empty
        if (self._parent_scene.model.state == WorldState.COMBAT) and (self._combat_ending_timer == -1):
            all_entities = self._parent_scene.model.get_all_entities()
            player_entities = [e for e in all_entities if e.team == "player"]
            if len(player_entities) == 0:
                self._process_defeat()

            elif len(player_entities) == len(all_entities):
                self._process_victory()

        if self._parent_scene.model.state == WorldState.VICTORY:
            self.victory_duration += delta_time
            if self.victory_duration > 3:
                self._game.memory.remove_troupe(self.enemy_troupe_id)
                for troupe in self._game.memory.troupes.values():
                    troupe.set_force_idle(False)
                self._parent_scene.ui.grid.move_units_to_grid()
                self.end_combat()

            # TODO - what is last death?
            if self.last_unit_death:
                # average the last positions of the last entity to die and the killer of that entity
                focus_point = (
                    (self.last_unit_death[0].pos[0] + self.last_unit_death[1].pos[0]) / 2,
                    (self.last_unit_death[0].pos[1] + self.last_unit_death[1].pos[1]) / 2,
                )
                # TODO: decouple this
                self._parent_scene.ui._worldview.camera.move_to_position(focus_point)

        if self._parent_scene.model.state == WorldState.MOVING_NEXT_ROOM:
            # move entities
            for i in self._parent_scene.model.get_all_entities():
                # cannot use move here because it is very buggy when entities are touching
                i.pos[0] += 5

            # TODO: find better way to calculate this value
            final = self._game.window.base_resolution[0] + 320 + 320
            terrain_offset = self._game.window.base_resolution[0] + 320

            # this is a giant hack because the game only supports
            # "one room" at a time, and everything needs to be in the
            # "primary" terrain.  to remove hack, one way to fix would
            # be to make sure game can support more than one terrain
            # and all game entities coordinates are independent of the
            # terrain.
            # when entities are in next room, swap terrains and idle
            if i.pos[0] >= final:
                for i in self._parent_scene.model.get_all_entities():
                    # cannot use move here because it is very buggy when entities are touching
                    i.pos[0] -= terrain_offset
                # TODO: decouple this
                self._parent_scene.ui._worldview.clamp_primary_terrain = True
                self._parent_scene.ui._worldview.camera.move(-terrain_offset - 148, 0)
                self._parent_scene.model.terrain.ignore_boundaries = False
                self._parent_scene.model.next_terrain.ignore_boundaries = False
                self._parent_scene.model.swap_terrains()
                self.reset()

    def begin_combat(self):
        self.generate_combat()
        self._parent_scene.model.state = WorldState.COMBAT
        for troupe in self._game.memory.troupes.values():
            troupe.set_force_idle(False)

    def reset(self):
        self._parent_scene.model.state = WorldState.IDLE
        self._combat_ending_timer = -1
        self.enemy_troupe_id = -1

    def begin_move_to_new_room(self):
        """
        Move Units to a new room

        """
        if self._parent_scene.model.state == WorldState.IDLE:
            self._parent_scene.model.state = WorldState.MOVING_NEXT_ROOM

            # TODO: prepare next room type here

            # allow camera to pan past terrain boundaries
            # TODO: decouple this
            self._parent_scene.ui._worldview.clamp_primary_terrain = False

            # ignore walls
            self._parent_scene.model.terrain.ignore_boundaries = True
            self._parent_scene.model.next_terrain.ignore_boundaries = True

        else:
            raise Exception("bad state change")

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
                if not self._parent_scene.model.terrain.check_tile_solid(pos):
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
        """
        Return dictionary of data for a random combat

        """
        if not self._game.data.combats:
            return {}

        # get possible combats
        level = self._game.memory.level
        combats = self._game.data.combats.values()
        possible_combats = []
        possible_combats_occur_rates = []
        for combat in combats:
            # ensure only combat for this level or lower and of desired type
            if combat["level_available"] <= level and combat["category"] == self.combat_category:
                possible_combats.append(combat)
                occur_rate = self._game.data.get_combat_occur_rate(combat["type"])
                possible_combats_occur_rates.append(occur_rate)

        return self._game.rng.choices(possible_combats, possible_combats_occur_rates)[0]

    def _process_defeat(self):
        """
        Process the defeat, such as removing morale

        """
        self.combat_ending_timer = 0
        self.state = WorldState.DEFEAT

    def _process_victory(self):
        """
        Process victory

        """
        self.combat_ending_timer = 0
        self.state = WorldState.VICTORY

    def end_combat(self):
        """
        End the combat

        """
        self._game.memory.set_game_speed(1)
        for troupe in self._game.memory.troupes.values():
            troupe.set_force_idle(True)
        self._process_new_injuries()
        self._parent_scene.model.state = WorldState.IDLE

    def _process_new_injuries(self):
        """
        Process new injuries and resulting deaths

        """
        remove_units = []
        injuries_before_death = self._game.data.config["unit_properties"]["injuries_before_death"]
        log = self._game_log.append

        for i, unit in enumerate(self._game.memory.player_troupe.units.values()):

            # do an update to ensure unit.alive is updated
            unit.update(0.0001)

            # add injury for units killed in combat
            if not unit.alive:
                unit.injuries += 1

                # remove unit from troupe if the unit took too many injuries
                if unit.injuries >= injuries_before_death:
                    remove_units.append(unit.id)
                    log(f"{unit.type} died due to their injuries.")
                else:
                    log(f"{unit.type} was injured in battle.")

        # remove units after since they can't be removed during iteration
        for unit in remove_units:
            self._game.memory.player_troupe.remove_unit(unit)
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core import PointLike
from scripts.core.constants import TILE_SIZE, WorldState
from scripts.core.debug import Timer
from scripts.scene_elements.commander import Commander
from scripts.scene_elements.entity import Entity
from scripts.scene_elements.particle_manager import ParticleManager
from scripts.scene_elements.projectile_manager import ProjectileManager
from scripts.scene_elements.terrain import Terrain
from scripts.scene_elements.troupe import Troupe
from scripts.scene_elements.unit import Unit

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["WorldModel"]


class WorldModel:
    """
    Manage Terrain and game entities

    * No drawing should be done here
    * Include common operations for game world state
    * Store data for the World Scene

    The model is like a chess set.  Something else (a controller) needs to query the state and *ask* the model to
    make changes.

    The model should be unaware of what combat is, and instead should offer an API that combat, or anything else,
    can change the state of the model without actually being aware of how the model works. This provides
    for cross-controller (room) needs.
    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("WorldModel initialised"):
            self._game = game
            self._parent_scene = parent_scene

            self._previous_state: WorldState = WorldState.CHOOSE_NEXT_ROOM
            self._state: WorldState = WorldState.CHOOSE_NEXT_ROOM
            self._next_state: Optional[WorldState] = None

            self.projectiles: ProjectileManager = ProjectileManager(self._game)
            self.particles: ParticleManager = ParticleManager()
            self.terrain: Terrain = Terrain(self._game, "plains")
            self.terrain.generate()
            self.next_terrain: Terrain = Terrain(self._game, "plains")
            self.next_terrain.generate()

            # units
            self.troupes: Dict[int, Troupe] = {}

            # player choices
            self.commander: Optional[Commander] = None

            # events
            self._event_deck: Dict = self._load_events([1])  # all available events
            self._priority_events: Dict = {}  # events to be prioritised
            self._turns_since_priority_event: int = 0

            # resources
            self.gold: int = 0
            self.rations: int = 0
            self.charisma: int = 0
            self.leadership: int = 0
            self.morale: int = 0

            # progress
            self.level: int = 1
            self.events_triggered_this_level: int = 0

            # generated values for later user
            self.level_boss: str = ""

            # history
            self._seen_bosses: List[str] = []

            # config
            self._game_speed: float = 1

            # add empty player troupe
            self.add_troupe(Troupe(self._game, "player", []))

    @property
    def boundaries(self):
        return self.terrain.boundaries

    @property
    def next_boundaries(self):
        # TODO: change this if rooms can move to other sides
        return self.next_terrain.boundaries.move(self.boundaries.width, 0)

    @property
    def total_boundaries(self):
        return self.boundaries.union(self.next_boundaries)

    @property
    def charisma_remaining(self) -> int:
        num_units = len(self.player_troupe.units)
        remaining = self.charisma - num_units
        return remaining

    def px_to_loc(self, pos: PointLike):
        """
        Convert map coordinates to tile coordinate

        * NOTE: map units are "pixels"
        """
        return self.terrain.px_to_loc(pos)

    def update(self, delta_time: float):
        self.particles.update(delta_time)
        self.projectiles.update(delta_time)
        for troupe in self.troupes.values():
            troupe.update(delta_time)

    def reset(self):
        self.particles = ParticleManager()
        self.projectiles = ProjectileManager(self._game)

        # units
        self.troupes = {}

        # player choices
        self.commander = None

        # events
        self._event_deck = self._load_events([1])  # all available events
        self._priority_events = {}  # events to be prioritised
        self._turns_since_priority_event = 0

        # resources
        self.gold = 0
        self.rations = 0
        self.charisma = 0
        self.leadership = 0
        self.morale = 0

        # progress
        self.level = 1

        # generated values for later user
        self.level_boss = ""

        # history
        self._seen_bosses = []

        # config
        self._game_speed = 1

    def swap_terrains(self):
        """
        Swap primary and next terrains
        """
        temp = self.terrain
        self.terrain = self.next_terrain
        self.next_terrain = temp

    def force_idle(self):
        self._parent_scene.ui.grid.move_units_to_grid()
        for troupe in self.troupes.values():
            troupe.set_force_idle(True)

    def amend_gold(self, amount: int) -> int:
        """
        Amend the current gold value by the given amount. Return remaining amount.
        """
        self.gold = max(0, self.gold + amount)
        return self.gold

    def amend_rations(self, amount: int) -> int:
        """
        Amend the current rations value by the given amount. Return remaining amount.
        """
        self.rations = max(0, self.rations + amount)
        return self.rations

    def amend_charisma(self, amount: int) -> int:
        """
        Amend the current charisma value by the given amount. Return remaining amount.
        """
        self.charisma = max(0, self.charisma + amount)
        return self.charisma

    def amend_leadership(self, amount: int) -> int:
        """
        Amend the current leadership value by the given amount. Return remaining amount.
        """
        self.leadership = max(0, self.leadership + amount)
        return self.leadership

    def amend_morale(self, amount: int) -> int:
        """
        Amend the current morale value by the given amount. Return remaining amount.
        """
        self.morale = max(0, self.morale + amount)
        return self.morale


    def _load_events(self, levels: Optional[List[int]] = None) -> Dict:
        # handle mutable default
        if levels is None:
            levels = [1, 2, 3, 4]  # all levels

        event_deck = {}
        events = self._game.data.events

        # add events
        for event in events.values():
            if event["level_available"] in levels:
                event_deck[event["type"]] = event

        return event_deck

    def generate_level_boss(self):
        """
        Generate the boss for the current level.
        """
        available_bosses = []

        for boss in self._game.data.bosses.values():
            if boss["level_available"] <= self.level and boss["type"] not in self._seen_bosses:
                available_bosses.append(boss["type"])

        chosen_boss = self._game.rng.choice(available_bosses)
        self.level_boss = chosen_boss

        self._seen_bosses.append(chosen_boss)

    def get_all_entities(self) -> List[Entity]:
        """
        Get a list of all entities
        """
        entities = []

        for troupe in self.troupes.values():
            entities += troupe.entities

        return entities

    def get_all_units(self) -> List[Unit]:
        """
        Get a list of all Units
        """
        units = []

        for troupe in self.troupes.values():
            for unit in troupe.units.values():
                units.append(unit)

        return units

    @property
    def player_troupe(self) -> Troupe:
        for troupe in self.troupes.values():
            if troupe.team == "player":
                return troupe

        # in case we cant find it at all!
        raise Exception("Tried to get player troupe but couldnt find it!")

    def add_troupe(self, troupe: Troupe) -> int:
        """
        Add a Troupe. Returns Troupe ID
        """
        id_ = self._game.memory.generate_id()
        self.troupes[id_] = troupe

        return id_

    def remove_troupe(self, id_: int):
        """
        Remove a Troupe from the game. Deletes Troupe.
        """
        try:
            troupe = self.troupes.pop(id_)
            troupe.remove_all_units()

        except KeyError:
            logging.warning(f"Tried to remove troupe id ({id_} but not found. Troupes:({self.troupes})")
            raise Exception

    def set_game_speed(self, speed: float):
        """
        Set the game speed. 1 is default.
        """
        self._game_speed = speed

    @property
    def game_speed(self) -> float:
        return self._game_speed

    @property
    def state(self) -> WorldState:
        return self._state

    @state.setter
    def state(self, state: WorldState):
        """
        Change the current state. Reset the controller for the given state.
        """
        # update previous state
        self._previous_state = self._state

        # reset the relevant scene
        if state == WorldState.TRAINING:
            self._parent_scene.training.reset()
        elif state == WorldState.INN:
            self._parent_scene.inn.reset()
        elif state == WorldState.COMBAT:
            self._parent_scene.combat.reset()
        elif state == WorldState.EVENT:
            self._parent_scene.event.reset()

        # update the state
        self._state = state

    @property
    def next_state(self) -> Optional[WorldState]:
        return self._next_state

    @next_state.setter
    def next_state(self, state: WorldState):
        self._next_state = state

    def go_to_next_state(self):
        """
        Transition to the state held in next_state and clear it.
        """
        self.state = self._next_state
        self._next_state = None

    @property
    def previous_state(self) -> WorldState:
        return self._previous_state


    def roll_for_event(self) -> bool:
        """
        Roll to see if an event will be triggered when transitioning between rooms. True if event due.
        """
        # check if we have hit the limit of events
        if (
                self.events_triggered_this_level
                >= self._game.data.config["world"]["max_events_per_level"]
        ):
            return False

        if self._game.rng.roll() < self._game.data.config["world"]["chance_of_event"]:
            return True

        # safety catch
        return False

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import ChooseRoomState, WorldState
from scripts.core.debug import Timer

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene


__all__ = ["ChooseRoomController"]


class ChooseRoomController(Controller):
    """
    Choose next room functionality and  data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """
    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("TrainingController initialised"):
            super().__init__(game, parent_scene)

            self.state: ChooseRoomState = ChooseRoomState.IDLE

            self.num_choices: int = 2
            self.choices: List[Tuple[str, bool]] = []  # (room_type, is_hidden)
            self.selected_room: Optional[str] = None
            self.current_index: int = 0

            self._generate_room_choices()

    def update(self, delta_time: float):
        if self._parent_scene.model.state == WorldState.MOVING_NEXT_ROOM:
            self._process_moving_to_new_room()

    def reset(self):
        self.state = ChooseRoomState.IDLE

        self.num_choices = 3
        self.choices = []  # (room_type, is_hidden)
        self.selected_room = None

        self._generate_room_choices()

    def _generate_room_choices(self):
        # reset existing
        self.choices = []

        # pick unique rooms
        room_weights = self._game.data.config["world"]["room_weights"]
        room_types = []
        for i in range(1000):
            room_type = self._game.rng.choices(list(room_weights.keys()), list(room_weights.values()), k=1)[0]

            if room_type not in room_types:
                room_types.append(room_type)

                # check if we have enough rooms
                if len(room_types) >= self.num_choices:
                    break

        # check for hidden
        chance_hidden = self._game.data.config["world"]["chance_room_type_hidden"]
        already_hidden = False
        for room_type in room_types:
            if self._game.rng.roll() < chance_hidden or already_hidden:
                self.choices.append((room_type, True))
                already_hidden = True  # only hide 1 room choice
            else:
                self.choices.append((room_type, False))

    def begin_move_to_new_room(self):
        """
        Move Units to a new room

        """
        if self._parent_scene.model.state == WorldState.CHOOSE_NEXT_ROOM:
            logging.info(f"Moving to new room ({self.selected_room}).")

            self._parent_scene.model.state = WorldState.MOVING_NEXT_ROOM

            # allow camera to pan past terrain boundaries
            self._parent_scene.ui._worldview.clamp_primary_terrain = False

            # ignore walls
            self._parent_scene.model.terrain.ignore_boundaries = True
            self._parent_scene.model.next_terrain.ignore_boundaries = True

        else:
            raise Exception("begin_move_to_new_room: Not in expected state.")

    def _process_moving_to_new_room(self):
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
            self._assign_room_state()
            self.reset()


    def _assign_room_state(self):
        """
        Assign state to WorldModel based on room selected
        """
        room = self.selected_room

        if room == "training":
            new_state = WorldState.TRAINING
        elif room == "combat":
            new_state = WorldState.COMBAT
        else:
            raise Exception(f"_assign_room_state: room type ({room}) not handled.")

        self._parent_scene.model.state = new_state
        logging.debug(f"WorldState updated to {new_state}.")



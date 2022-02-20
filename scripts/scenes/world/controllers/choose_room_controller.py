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

    def update(self, delta_time: float):
        pass

    def reset(self):
        pass

    def generate_room_choices(self):
        # reset existing
        self.choices = []

        # pick rooms
        room_weights = self._game.data.config["world"]["room_weights"]
        room_types = self._game.rng.choices(list(room_weights.keys()), list(room_weights.values()), k=self.num_choices)

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
            self._parent_scene.model.state = WorldState.MOVING_NEXT_ROOM

            # allow camera to pan past terrain boundaries
            self._parent_scene.ui._worldview.clamp_primary_terrain = False

            # ignore walls
            self._parent_scene.model.terrain.ignore_boundaries = True
            self._parent_scene.model.next_terrain.ignore_boundaries = True

        else:
            raise Exception("begin_move_to_new_room: Not in expected state.")




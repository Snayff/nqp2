from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import snecs

from nqp.base_classes.controller import Controller
from nqp.core import queries
from nqp.core.constants import ChooseRoomState, GameSpeed, WorldState
from nqp.core.debug import Timer
from nqp.world_elements.entity_components import Position

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

    from nqp.core.game import Game
    from nqp.scenes.world.scene import WorldScene


__all__ = ["ChooseRoomController"]


class ChooseRoomController(Controller):
    """
    Choose next room functionality and  data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("TrainingController: initialised"):
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
            if self._game.rng.roll() < chance_hidden and not already_hidden:
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
            self._game.memory.set_game_speed(GameSpeed.FASTEST)

            # allow camera to pan past terrain boundaries
            self._parent_scene.ui._worldview.clamp_primary_terrain = False

            # ignore walls
            self._parent_scene.model.terrain.ignore_boundaries = True
            self._parent_scene.model.next_terrain.ignore_boundaries = True

            # update camera
            target_entity = self._parent_scene.model.player_troupe.entities[0]
            self._parent_scene.ui._worldview.camera.set_target_entity(target_entity)

            # TODO: find better way to calculate this value
            final = self._game.window.base_resolution[0] + 320 + 320

            # give entities target to move to
            for entity, (ai, position) in queries.ai_position:
                behaviour = ai.behaviour
                new_x = max(position.x + 50, final)  # can't set to final else wont find a path
                behaviour.target_position = (new_x, position.y)

        else:
            raise Exception("begin_move_to_new_room: Not in expected state.")

    def _process_moving_to_new_room(self):

        # TODO: find better way to calculate this value
        final = self._game.window.base_resolution[0] + 320 + 320
        terrain_offset = self._game.window.base_resolution[0] + 320

        # TODO - remove when pathfinding is fixed
        # manually move to new room
        for entity, (position,) in queries.position:
            position.x += 5

        # get position of first entity for reference
        position = snecs.entity_component(self._parent_scene.model.get_all_entities()[0], Position)

        # this is a giant hack because the game only supports
        # "one room" at a time, and everything needs to be in the
        # "primary" terrain.  to remove hack, one way to fix would
        # be to make sure game can support more than one terrain
        # and all game entities coordinates are independent of the
        # terrain.
        # when entities are in next room, swap terrains and idle
        if position.x >= final:
            for entity in self._parent_scene.model.get_all_entities():
                # cannot use move here because it is very buggy when entities are touching
                position = snecs.entity_component(entity, Position)
                position.x -= terrain_offset

            # TODO: decouple this
            self._parent_scene.ui._worldview.clamp_primary_terrain = True
            self._parent_scene.ui._worldview.camera.move(-terrain_offset - 148, 0)
            self._parent_scene.model.terrain.ignore_boundaries = False
            self._parent_scene.model.next_terrain.ignore_boundaries = False
            self._parent_scene.model.swap_terrains()
            self._parent_scene.ui._worldview.camera.set_target_entity(None)
            self._assign_room_state()
            self.reset()
            self._game.memory.set_game_speed(GameSpeed.NORMAL)

    def _assign_room_state(self):
        """
        Assign state to WorldModel based on room selected and if event is due
        """
        room = self.selected_room
        event_due = self._parent_scene.model.roll_for_event()

        if room == "training":
            new_room_state = WorldState.TRAINING
        elif room == "combat":
            new_room_state = WorldState.COMBAT
        elif room == "inn":
            new_room_state = WorldState.INN
        else:
            raise Exception(f"_assign_room_state: room type ({room}) not handled.")

        if event_due:
            self._parent_scene.model.state = WorldState.EVENT
            self._parent_scene.model.next_state = new_room_state
        else:
            self._parent_scene.model.state = new_room_state

        self._parent_scene.ui.rebuild_ui()

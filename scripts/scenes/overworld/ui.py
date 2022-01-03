from __future__ import annotations

import itertools
import logging
import math
from typing import TYPE_CHECKING

import pygame
import pytweening

from scripts.core import utility
from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, Direction, FontType, NodeType, OverworldState, SceneType
from scripts.ui_elements.frame import Frame

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union
    from scripts.core.game import Game
    from scripts.core.base_classes.scene import Scene


__all__ = ["OverworldUI"]


class OverworldUI(UI):
    """
    Represents the overworld UI.
    """

    def __init__(self, game: Game, parent_scene: Scene):
        super().__init__(game, parent_scene, True)

        self._wait_time_before_move: float = 0.5
        self.max_travel_time: float = 2.2
        self.current_travel_time: float = 0.0
        self._wait_time_after_arrival: float = 1.0
        self._current_wait_time: float = 0.0

        self._total_travel_time: float = 0.0
        self._frame_timer: float = 0
        self._boss_x: int = 0
        self._boss_y: int = 0

        # N.B. Doesnt use Panels to handle input.

        self.set_instruction_text(
            "Choose where you will go next. Up/Down for moving between rings and Left/Right for clockwise "
            "and anti-clockwise."
        )

    def update(self, delta_time: float):
        super().update(delta_time)

        state = self.game.overworld.state

        # tick frame
        self._frame_timer += delta_time
        # FIXME - temporary looping frame logic
        while self._frame_timer > 0.66:
            self._frame_timer -= 0.66

        # get boss draw pos
        if state == OverworldState.BOSS_APPROACHING:
            # init boss approaching
            if self._boss_x == 0 and self._boss_y == 0:
                self._boss_x = self.game.overworld.node_container.boss_pos[0]
                self._boss_y = self.game.overworld.node_container.boss_pos[1]

                self.elements["boss_notification"].is_active = True

            # update timer
            self._total_travel_time += delta_time

            total_time = self._total_travel_time
            wait_before = self._wait_time_before_move
            wait_after = self._wait_time_after_arrival
            max_duration = self.max_travel_time

            if total_time > (wait_before + max_duration + wait_after):
                # trigger boss fight
                self.game.overworld.node_container.selected_node.type = NodeType.BOSS_COMBAT
                self.game.overworld.node_container.trigger_current_node()

                self.game.overworld.state = OverworldState.READY

            elif total_time > (wait_before + max_duration):
                # make boss wait by player
                selected_node = self.game.overworld.node_container.selected_node
                target_x = selected_node.pos[0] - (DEFAULT_IMAGE_SIZE // 2)
                target_y = selected_node.pos[1] - (DEFAULT_IMAGE_SIZE // 2)
                self._boss_x = target_x
                self._boss_y = target_y

            elif total_time > wait_before:
                # move boss to player
                self.current_travel_time += delta_time

                # determine amount to use for lerp
                percent_time_complete = min(1.0, self.current_travel_time / self.max_travel_time)

                # update selection position
                lerp_amount = pytweening.easeInQuad(percent_time_complete)
                selected_node = self.game.overworld.node_container.selected_node
                target_x = selected_node.pos[0] - (DEFAULT_IMAGE_SIZE // 2)
                target_y = selected_node.pos[1] - (DEFAULT_IMAGE_SIZE // 2)
                self._boss_x = utility.lerp(self._boss_x, target_x, lerp_amount)
                self._boss_y = utility.lerp(self._boss_y, target_y, lerp_amount)

            elif total_time < wait_before:
                # make boss wait after spawn
                pass

        else:
            # reset timers
            self.current_travel_time = 0
            self._total_travel_time = 0

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        state = self.game.overworld.state

        if state == OverworldState.READY:

            node_container = self.game.overworld.node_container

            # match the nodes with the most accurate combination of directions possible
            bordering_nodes = [
                (Direction.DOWN, node_container.selected_node.connected_inner_node),
                (Direction.UP, node_container.selected_node.connected_outer_node),
                (Direction.LEFT, node_container.lr_node(Direction.LEFT)),
                (Direction.RIGHT, node_container.lr_node(Direction.RIGHT)),
            ]
            bordering_nodes = [
                (
                    n[0],
                    math.degrees(
                        math.atan2(
                            n[1].pos[1] - node_container.selected_node.pos[1],
                            -(n[1].pos[0] - node_container.selected_node.pos[0]),
                        )
                    ),
                )
                if n[1]
                else (n[0], None)
                for n in bordering_nodes
            ]
            dirs = [("left", 0), ("right", 180), ("up", -90), ("down", 90)]

            best_combo = [0, 999999]
            permutations = list(itertools.permutations(bordering_nodes))
            for j, perm in enumerate(permutations):
                perm_total = 0
                for i, d in enumerate(dirs):
                    if perm[i][1] == None:
                        continue
                    else:
                        a = perm[i][1]
                        while abs(a - d[1]) > 180:
                            if a > d[1]:
                                a -= 360
                            else:
                                a += 360
                        dif = abs(a - d[1])
                        perm_total += dif
                if perm_total < best_combo[1]:
                    best_combo = [j, perm_total]

            key_assignments = {}
            for i, key in enumerate(permutations[best_combo[0]]):
                if key[1]:
                    key_assignments[dirs[i][0]] = key[0]

            for dir in ["left", "right", "up", "down"]:
                if self.game.input.states[dir]:
                    self.game.input.states[dir] = False
                    if dir in key_assignments:
                        node_container.select_next_node(key_assignments[dir])
                        node_container.roll_for_event()

            if self.game.input.states["view_troupe"]:
                self.game.input.states["view_troupe"] = False
                self.game.change_scene(SceneType.VIEW_TROUPE)

            if self.game.input.states["select"]:
                self.game.input.states["select"] = False
                if not node_container.selected_node.is_complete:
                    node_container.trigger_current_node()

            # trigger event notification message
            node_container = self.game.overworld.node_container
            if node_container.show_event_notification:
                if node_container.event_notification_timer > 0:
                    self.elements["event_notification"].is_active = True
                    delta_time = self.game.window.delta_time
                    node_container.event_notification_timer -= delta_time
                else:
                    self.elements["event_notification"].is_active = False
                    node_container.show_event_notification = False

                    self.game.change_scene(SceneType.EVENT)

    def render(self, surface: pygame.surface):
        state = self.game.overworld.state

        # show core info
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

        # show boss
        if state == OverworldState.BOSS_APPROACHING:
            # determine animation frame
            frame = int(self._frame_timer * 6)

            # get boss animation
            boss = self.game.memory.level_boss
            image = self.game.assets.boss_animations[boss]["move"][frame]

            # draw boss
            surface.blit(image, (self._boss_x, self._boss_y))

    def rebuild_ui(self):
        super().rebuild_ui()

        overworld_map = self.game.overworld
        create_font = self.game.assets.create_font

        if overworld_map.state == OverworldState.LOADING:
            # draw loading screen
            current_x = 10
            current_y = self.game.window.height - 20
            frame = Frame(
                (current_x, current_y), font=create_font(FontType.NEGATIVE, "Loading..."), is_selectable=False
            )
            self.elements["loading_message"] = frame

        else:
            # N.B.  most drawing happens in the node_container

            # draw resources
            self.rebuild_resource_elements()

            # draw days remaining
            days = self.game.memory.days_until_boss
            font = self.game.assets.create_font(FontType.DISABLED, f"Days remaining:{days}")
            frame = Frame((0, 20), font=font, is_selectable=False)
            self.elements["days_remaining"] = frame

            # draw event notification
            notification = "Something is afoot!"
            current_x = 10
            current_y = int(self.game.window.height / 2)
            frame = Frame(
                (current_x, current_y), font=create_font(FontType.NOTIFICATION, notification), is_selectable=False
            )
            frame.is_active = False  # dont show until activated
            self.elements["event_notification"] = frame

            # draw boss notification
            notification = "The enemy approaches!"
            current_x = 10
            current_y = int(self.game.window.height / 2)
            frame = Frame(
                (current_x, current_y), font=create_font(FontType.NOTIFICATION, notification), is_selectable=False
            )
            frame.is_active = False
            self.elements["boss_notification"] = frame

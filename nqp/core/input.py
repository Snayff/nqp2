from __future__ import annotations

import dataclasses
import logging
import time
from typing import Mapping, Tuple, TYPE_CHECKING

import pygame
from pygame.locals import *

from .constants import GamepadAxes, GamepadButton
from .debug import Timer

if TYPE_CHECKING:
    from nqp.core.game import Game

__all__ = ["Input"]


@dataclasses.dataclass
class ControllerConfig:
    deadzone: float
    axes: Mapping[int, GamepadAxes]
    hat: Mapping[int, Tuple[GamepadButton, GamepadButton]]
    buttons: Mapping[int, GamepadButton]


# specific to xbox gamepad layout, should not be changed by player
# add more configs for other gamepad types: ps3,4,5, switch, etc
xbox_gamepad_config = ControllerConfig(
    deadzone=0.25,
    axes={
        0: GamepadAxes.LEFT_X,
        1: GamepadAxes.LEFT_Y,
        # 2: None,  # l. shoulder
        3: GamepadAxes.RIGHT_X,
        4: GamepadAxes.RIGHT_Y,
        # 5: None,  # r. shoulder
    },
    hat={
        0: (GamepadButton.LEFT, GamepadButton.RIGHT),
        1: (GamepadButton.DOWN, GamepadButton.UP),
    },
    buttons={
        0: GamepadButton.SOUTH,
        1: GamepadButton.EAST,
        2: GamepadButton.WEST,
        3: GamepadButton.NORTH,
        4: GamepadButton.LEFT_SHOULDER_1,
        5: GamepadButton.RIGHT_SHOULDER_1,
        6: GamepadButton.SELECT_OR_BACK,
        7: GamepadButton.START,
        8: GamepadButton.LEFT_STICK,
        9: GamepadButton.RIGHT_STICK,
    },
)

# generic mapping for gamepad buttons to game input labels
# if the player wants to change config, this would need to be changed
gamepad_label_map = {
    GamepadButton.UP: "up",
    GamepadButton.LEFT: "left",
    GamepadButton.DOWN: "down",
    GamepadButton.RIGHT: "right",
    GamepadButton.EAST: "cancel",
    GamepadButton.SOUTH: "select",
    GamepadButton.NORTH: "view_troupe",
}

# map analog axis to digital buttons
gamepad_axis_direction_map = {
    GamepadAxes.LEFT_X: [GamepadButton.LEFT, GamepadButton.RIGHT],
    GamepadAxes.LEFT_Y: [GamepadButton.UP, GamepadButton.DOWN],
}


class Input:
    def __init__(self, game: Game):
        with Timer("Input: initialised"):

            self._game: Game = game

            self.states = {
                "right": False,
                "left": False,
                "up": False,
                "down": False,
                "hold_right": False,
                "hold_left": False,
                "hold_up": False,
                "hold_down": False,
                "select": False,
                "cancel": False,
                "view_troupe": False,
                "shift": False,
                "ctrl": False,
                "backspace": False,
                "toggle_dev_console": False,
                "typing_enter": False,
                "tab": False,
                "speed_slow": False,
                "speed_normal": False,
                "speed_fast": False,
                "speed_fastest": False,
            }

            self.mouse_state = {"left": False}

            self.mode = "default"

            self.char_buffer = ""
            self.backspace_hold = 0

            self.mouse_moved = False
            self.mouse_pos: pygame.Vector2 = pygame.Vector2(0, 0)
            self.mouse_pos_raw: pygame.Vector2 = self.mouse_pos
            self._old_mouse: pygame.Vector2 = self.mouse_pos_raw

            self._gamepads = dict()
            self._scan_gamepads()

    def soft_reset(self):
        """
        Resets inputs that should only be activated for 1 frame.
        """
        self.states["select"] = False
        self.states["cancel"] = False
        self.mouse_state["left"] = False

    def reset(self):
        """
        Set all input to false.
        """
        for key in self.states.keys():
            self.states[key] = False

    def unload_chars(self):
        chars = self.char_buffer
        self.char_buffer = []
        return chars

    def update(self, delta_time: float):
        self.soft_reset()

        self.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self.mouse_pos_raw = self.mouse_pos
        self.mouse_pos[0] *= self._game.window.base_resolution[0] / self._game.window.scaled_resolution[0]
        self.mouse_pos[1] *= self._game.window.base_resolution[1] / self._game.window.scaled_resolution[1]
        self.mouse_moved = self.mouse_pos_raw != self._old_mouse
        self._old_mouse = self.mouse_pos_raw

        chars = [
            ".",
            "-",
            "_",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        ]

        if self.mode == "typing":
            if self.states["backspace"]:
                self.backspace_hold += self._game.window.delta_time
                if self.backspace_hold > 0.7:
                    self.backspace_hold -= 0.035
                    self.char_buffer.append("backspace")
            else:
                self.backspace_hold = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                self._game.quit()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_state["left"] = True

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self._game.quit()

                if event.key in [K_LSHIFT, K_RSHIFT]:
                    self.states["shift"] = True

                if event.key in [K_LCTRL, K_RCTRL]:
                    self.states["ctrl"] = True

                if event.key == K_BACKSPACE:
                    self.states["backspace"] = True

                if event.key == K_BACKQUOTE:
                    self.states["toggle_dev_console"] = True

                if event.key == K_TAB:
                    self.states["tab"] = True

                if self.mode == "typing":
                    if event.key == K_RETURN:
                        self.states["typing_enter"] = True

            if event.type == KEYUP:
                if event.key in [K_LSHIFT, K_RSHIFT]:
                    self.states["shift"] = False

                if event.key == K_BACKSPACE:
                    self.states["backspace"] = False

            # input outside of typing
            if self.mode == "default":
                if event.type == KEYDOWN:
                    if event.key == K_x:
                        self.states["cancel"] = True

                    if event.key == K_RIGHT:
                        self.states["right"] = True
                        self.states["hold_right"] = True

                    if event.key == K_LEFT:
                        self.states["left"] = True
                        self.states["hold_left"] = True

                    if event.key == K_UP:
                        self.states["up"] = True
                        self.states["hold_up"] = True

                    if event.key == K_DOWN:
                        self.states["down"] = True
                        self.states["hold_down"] = True

                    if event.key == K_RETURN:
                        self.states["select"] = True

                    if event.key == K_v:
                        self.states["view_troupe"] = True

                    if event.key == K_F1:
                        self.states["speed_slow"] = True

                    if event.key == K_F2:
                        self.states["speed_normal"] = True

                    if event.key == K_F3:
                        self.states["speed_fast"] = True

                    if event.key == K_F4:
                        self.states["speed_fastest"] = True

                if event.type == KEYUP:
                    if event.key == K_RIGHT:
                        self.states["hold_right"] = False

                    if event.key == K_LEFT:
                        self.states["hold_left"] = False

                    if event.key == K_UP:
                        self.states["hold_up"] = False

                    if event.key == K_DOWN:
                        self.states["hold_down"] = False

                if event.type == JOYBUTTONDOWN:
                    button = xbox_gamepad_config.buttons[event.button]
                    label = gamepad_label_map.get(button)
                    if label:
                        self.states[label] = True
                        self.states["hold_" + label] = True

                if event.type == JOYBUTTONUP:
                    button = xbox_gamepad_config.buttons[event.button]
                    label = gamepad_label_map.get(button)
                    if label:
                        self.states["hold_" + label] = False

                if event.type == JOYHATMOTION:
                    for axis, value in enumerate(event.value):
                        endstops = xbox_gamepad_config.hat[axis]
                        button = None
                        if value == -1:
                            button = endstops[0]
                        elif value == 1:
                            button = endstops[1]
                        if button:
                            label = gamepad_label_map[button]
                            self.states[label] = True
                            self.states["hold_" + label] = True
                        else:
                            for button in endstops:
                                label = gamepad_label_map[button]
                                self.states["hold_" + label] = False

                if event.type == JOYAXISMOTION:
                    axis = xbox_gamepad_config.axes[event.axis]
                    endstops = gamepad_axis_direction_map.get(axis)
                    if endstops is not None:
                        if abs(event.value) >= xbox_gamepad_config.deadzone:
                            button = None
                            if event.value < 0:
                                button = endstops[0]
                            elif event.value > 0:
                                button = endstops[1]
                            if button:
                                label = gamepad_label_map[button]
                                hold_label = "hold_" + label
                                if not self.states[hold_label]:
                                    self.states[label] = True
                                self.states[hold_label] = True
                        else:
                            for button in endstops:
                                label = gamepad_label_map[button]
                                self.states["hold_" + label] = False

            elif self.mode == "typing":
                if event.type == KEYDOWN:
                    for char in chars:
                        if event.key == ord(char):
                            if self.states["shift"]:
                                char = char.upper()
                                if char == "-":
                                    char = "_"
                            self.char_buffer.append(char)

                    if event.key == K_BACKSPACE:
                        self.char_buffer.append("backspace")

                    if event.key == K_SPACE:
                        self.char_buffer.append(" ")

    def _scan_gamepads(self):
        for index in range(pygame.joystick.get_count()):
            gamepad = pygame.joystick.Joystick(index)
            gamepad.init()
            # if the Joystick object is deleted, then event loop
            # will not have joystick events, so we need to keep a ref.
            self._gamepads[gamepad.get_guid()] = gamepad

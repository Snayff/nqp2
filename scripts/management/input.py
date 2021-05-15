from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame.locals import *

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Input"]


class Input:
    def __init__(self, game: Game):
        self.game: Game = game

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
        }

    def soft_reset(self):
        self.states["select"] = False
        self.states["cancel"] = False

    def update(self):
        self.soft_reset()

        for event in pygame.event.get():
            if event.type == QUIT:
                self.game.quit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.game.quit()

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

            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.states["hold_right"] = False

                if event.key == K_LEFT:
                    self.states["hold_left"] = False

                if event.key == K_UP:
                    self.states["hold_up"] = False

                if event.key == K_DOWN:
                    self.states["hold_down"] = False

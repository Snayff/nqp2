from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["EventUI"]


class EventUI:
    """
    Represent the UI of the Event screen.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.selected_option: int = 0

    def update(self):
        options = self.game.event.active_event["options"]

        if self.game.input.states["left"]:
            self.game.input.states["left"] = False
            self.selected_option -= 1

        if self.game.input.states["right"]:
            self.game.input.states["right"] = False
            self.selected_option += 1

        # correct selection index for looping
        if self.selected_option < 0:
            self.selected_option = len(options) - 1
        if self.selected_option >= len(options):
            self.selected_option = 0

    def render(self, surface: pygame.surface):
        pass

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.ui.event import EventUI

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Event"]


class Event:
    """
    Handles Event interactions and consolidates the rendering. Event is used to give players a text choice.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: EventUI = EventUI(game)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

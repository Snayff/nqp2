from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.management.game import Game


class Overworld:
    """
    Represents the overworld view and handles related interactions.
    """

    def __init__(self, game: Game):
        self.game: Game = game


    def update(self):
        pass

    def render(self):
        pass

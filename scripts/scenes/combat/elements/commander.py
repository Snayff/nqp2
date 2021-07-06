from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game


__all__ = ["Commander"]


class Commander:
    def __init__(self, game: Game, name: str):
        self.game: Game = game

        data = self.game.data.commanders[name]

        self.name = name
        self.charisma = data["charisma"]
        self.leadership = data["leadership"]
        # allies not stored here as they are held in the Troupe



from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game


__all__ = ["Commander"]


class Commander:
    def __init__(self, game: Game, type: str):
        self.game: Game = game

        data = self.game.data.commanders[type]

        self.type = type
        self.charisma = data["charisma"]  # number of units that can be recruited
        self.leadership = data["leadership"]  # points to spend to deploy units in combat
        # N.B. allies not stored here as they are held in the Troupe

    @property
    def charisma_remaining(self) -> int:
        num_units = len(self.game.memory.player_troupe.units)
        remaining = self.charisma - num_units

        return remaining

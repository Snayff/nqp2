from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game


__all__ = ["Commander"]


class Commander:
    def __init__(self, game: Game, type_: str):
        self._game: Game = game

        self.type = type_
        # N.B. allies not stored here as they are held in the Troupe

        data = self._game.data.commanders[type_]
        self.name = data["name"]

    @property
    def charisma_remaining(self) -> int:
        num_units = len(self._game.memory.player_troupe.units)
        remaining = self._game.memory.charisma - num_units

        return remaining
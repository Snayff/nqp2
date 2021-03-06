from __future__ import annotations

from typing import List, TYPE_CHECKING

from nqp.world_elements.item import Item

if TYPE_CHECKING:
    from nqp.core.game import Game


__all__ = ["Commander"]


class Commander:
    def __init__(self, game: Game, type_: str):
        # TODO - is this needed? What is it doing for us?
        self._game: Game = game

        self.type = type_
        # N.B. allies not stored here as they are held in the Troupe

        data = self._game.data.commanders[type_]
        self.name: str = data["name"]
        self.items: List[Item] = [game.data.create_item(name) for name in data["items"]]

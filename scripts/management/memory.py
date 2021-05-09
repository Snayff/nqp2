from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.elements.card_collection import CardCollection

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “screens”. E.g. money.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.deck: CardCollection = CardCollection(game)
        self.deck.generate(20)

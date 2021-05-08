from __future__ import annotations
from scripts.elements.card_collection import CardCollection



__all__ = ["Memory"]


class Memory:
    def __init__(self, game):
        self.game = game

        self.deck = CardCollection(game)
        self.deck.generate(20)

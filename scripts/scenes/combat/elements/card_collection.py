import random

from .card import Card


class CardCollection:
    def __init__(self, game):
        self.game = game
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self):
        # FIXME - this is a stub
        pass

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count=1, to=None):
        drawn_cards = []

        for i in range(count):
            if len(self.cards):
                drawn_cards.append(self.cards.pop(0))

        new_col = self.copy()
        new_col.cards = drawn_cards

        if not to:
            return new_col

        else:
            to.merge(new_col)
            return to

    def merge(self, card_col):
        self.cards += card_col.cards

    # just a tool for now
    def generate_units(self, count):
        for i in range(count):
            self.add_card(Card(self.game, "spearman"))

    # also just a tool for now
    def generate_actions(self, count):
        for i in range(count):
            self.add_card(Card(self.game, "fireball"))

    def copy(self):
        new_col = CardCollection(self.game)
        for card in self.cards:
            new_col.add_card(card.copy())
        return new_col

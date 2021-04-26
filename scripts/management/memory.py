from scripts.elements.card_collection import CardCollection

class Memory:
    def __init__(self, game):
        self.game = game

        self.deck = CardCollection(game)
        self.deck.generate(20)

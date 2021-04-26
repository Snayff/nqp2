from scripts.constants import CombatState

class CombatUI:
    def __init__(self, game):
        self.game = game

        self.selected_card = 0

    def update(self):
        cards = self.game.combat.hand.cards

        if self.game.input.states['left']:
            self.game.input.states['left'] = False
            self.selected_card -= 1
            if self.selected_card < 0:
                self.selected_card = len(cards) - 1

        if self.game.input.states['right']:
            self.game.input.states['right'] = False
            self.selected_card += 1
            if self.selected_card >= len(cards):
                self.selected_card = 0

    def render(self, surf):
        cards = self.game.combat.hand.cards

        if self.game.combat.state != CombatState.WATCH:
            start_pos = self.game.window.display.get_width() // 2 - (len(cards) - 1) * 30

            for i, card in enumerate(cards):
                height_offset = 0
                if self.selected_card == i:
                    height_offset = -12

                card.render(surf, (start_pos + i * 60 - 25, 300 + height_offset))

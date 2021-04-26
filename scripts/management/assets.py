from scripts.ui.text import Font

class Assets:
    def __init__(self, game):
        self.game = game

        self.fonts = {
            'small_red': Font('assets/fonts/small_font.png', (255, 0, 0))
        }

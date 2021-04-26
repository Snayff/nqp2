import pygame

class Card:
    def __init__(self, game, card_type):
        self.game = game
        self.type = card_type

    def copy(self):
        return Card(self.game, self.type)

    def render(self, surf, offset=(0, 0), render_mode='hand'):
        if render_mode == 'hand':
            size = [50, 70]

            # use a rect for now
            r = pygame.Rect(offset[0], offset[1], size[0], size[1])
            pygame.draw.rect(surf, (255, 255, 255), r)
            pygame.draw.rect(surf, (255, 0, 0), r, 1)
            self.game.assets.fonts['small_red'].render(self.type, surf, (offset[0] + 3, offset[1] + 3))

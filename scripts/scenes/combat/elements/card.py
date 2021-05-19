import pygame


class Card:
    def __init__(self, game, card_type):
        self.game = game
        self.type = card_type
        self.cost = 3

    def copy(self):
        return Card(self.game, self.type)

    def render(self, surface: pygame.Surface, offset=(0, 0), render_mode="hand"):
        if render_mode == "hand":
            size = [50, 70]

            # use a rect for now
            r = pygame.Rect(offset[0], offset[1], size[0], size[1])
            pygame.draw.rect(surface, (255, 255, 255), r)
            pygame.draw.rect(surface, (255, 0, 0), r, 1)
            self.game.assets.fonts["warning"].render(self.type, surface, (offset[0] + 3, offset[1] + 3))

import pygame


class Card:
    def __init__(self, game, card_type=None, troupe_src=None, troupe_id=None):
        # card_type is specified for action card while troupe_src and troupe_id are specified for troupe cards
        self._game = game
        self.action_type = card_type
        self.troupe_src = troupe_src
        self.troupe_id = troupe_id

    def copy(self):
        return Card(self._game, self.action_type, self.troupe_src, self.troupe_id)

    @property
    def unit(self):
        if not self.action_type:
            return self.troupe_src.units[self.troupe_id]
        else:
            return None

    @property
    def cost(self):
        return 3

    @property
    def type(self):
        if not self.action_type:
            return self.troupe_src.units[self.troupe_id].type
        else:
            return self.action_type

    @property
    def name(self):
        # this will have different logic later
        return self.type

    def render(self, surface: pygame.Surface, offset=(0, 0), render_mode="hand"):
        if render_mode == "hand":
            size = [50, 70]

            # use a rect for now
            r = pygame.Rect(offset[0], offset[1], size[0], size[1])
            pygame.draw.rect(surface, (255, 255, 255), r)
            pygame.draw.rect(surface, (255, 0, 0), r, 1)
            self._game.assets.fonts["warning"].render(self.type, surface, (offset[0] + 3, offset[1] + 3))

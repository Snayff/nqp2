import pygame


class UIButton:
    def __init__(self, game, content, pos, push_down=True, size=[10, 10], colour=(255, 255, 255)):
        self._game = game
        self.pos = list(pos)
        self.content = content
        self.colour = colour

        if type(self.content) != str:
            size = self.content.get_size()
        self.size = size

        self.push_down = push_down
        self.push_timer = 0

    @property
    def pressed(self):
        r = pygame.Rect(*self.pos, *self.size)
        if r.collidepoint(self._game.input.mouse_pos):
            if self._game.input.mouse_state["left"]:
                self.push_timer = 0.2
                return True
        return False

    def update(self, delta_time: float):
        self.push_timer = max(0, self.push_timer - delta_time)

    def draw(self, surf, offset=(0, 0)):
        offset = list(offset)
        if self.push_timer:
            offset[1] += 1
        if type(self.content) != str:
            surf.blit(self.content, (self.pos[0] + offset[0], self.pos[1] + offset[1]))
        else:
            r = pygame.Rect(self.pos[0] + offset[0], self.pos[1] + offset[1], *self.size)
            pygame.draw.rect(surf, self.colour, r, width=1)
            self._game.assets._fonts["default"].draw(
                self.content,
                surf,
                (
                    self.pos[0]
                    + offset[0]
                    + (self.size[0] - self._game.assets._fonts["default"].width(self.content)) // 2,
                    self.pos[1] + offset[1] + (self.size[1] - self._game.assets._fonts["default"].line_height) // 2,
                ),
            )

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from nqp.core.game import Game


class UIButton:
    def __init__(
        self,
        game: Game,
        content,
        pos: pygame.Vector2,
        push_down: bool = True,
        size: pygame.Vector2 = pygame.Vector2(10, 10),
        colour=(255, 255, 255),
    ):
        self._game = game
        self.pos: pygame.Vector2 = pos
        self.content = content
        self.colour = colour

        if type(self.content) != str:
            size = self.content.get_size()
        self.size = size

        self.push_down = push_down
        self.push_timer: float = 0

    @property
    def pressed(self):
        r = pygame.Rect(*self.pos, *self.size)
        if r.collidepoint((self._game.input.mouse_pos.x, self._game.input.mouse_pos.y)):
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
            surf.blit(self.content, (self.pos.x + offset[0], self.pos.y + offset[1]))
        else:
            r = pygame.Rect(self.pos.x + offset[0], self.pos.y + offset[1], *self.size)
            pygame.draw.rect(surf, self.colour, r, width=1)
            self._game.visual._fonts["default"].draw(
                self.content,
                surf,
                (
                    self.pos.x
                    + offset[0]
                    + (self.size.x - self._game.visual._fonts["default"].width(self.content)) // 2,
                    self.pos.y + offset[1] + (self.size.y - self._game.visual._fonts["default"].line_height) // 2,
                ),
            )

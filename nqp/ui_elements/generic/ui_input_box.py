from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import FontType

if TYPE_CHECKING:
    from nqp.core.game import Game


# TODO - add numpad support
# TODO - add special character support, particularly - | .
# TODO - handle blank input fields


class UIInputBox:
    def __init__(
            self, 
            game,
            size: pygame.Vector2,
            pos: pygame.Vector2 = pygame.Vector2(0, 0),
            colour=(255, 255, 255),
            input_type="all",
            text="",
            font=None
    ):
        self._game: Game = game
        self.size: pygame.Vector2 = size
        self.pos: pygame.Vector2 = pos
        self.colour = colour

        if input_type == "detect":
            if type(text) == int:
                input_type = "int"
            elif type(text) == float:
                input_type = "float"
            else:
                input_type = "lower"

        self.input_type = input_type

        self.previous_input_mode = None
        self.padding = 3
        self.focused = False

        if not font:
            font = self._game.visual.create_font(FontType.DEFAULT, str(text))
        self.font = font

        # assign font pos
        self.font.pos = pygame.Vector2(self.pos.x + self.padding, self.pos.y + (self.size.y - self.font.line_height) // 2)

    @property
    def value(self):
        if self.input_type == "int":
            return int(self.font.text)
        if self.input_type == "float":
            return float(self.font.text)
        else:
            return self.font.text

    @property
    def should_focus(self, offset=(0, 0)):
        if not self.focused:
            r = pygame.Rect(self.pos.x - offset[0], self.pos.y - offset[1], self.size.x, self.size.y)
            if r.collidepoint((self._game.input.mouse_pos.x, self._game.input.mouse_pos.y)):
                if self._game.input.mouse_state["left"]:
                    return True

            return False

        else:
            r = pygame.Rect(self.pos.x - offset[0], self.pos.y - offset[1], self.size.x, self.size.y)
            if not r.collidepoint((self._game.input.mouse_pos.x, self._game.input.mouse_pos.y)):
                if self._game.input.mouse_state["left"]:
                    return False

            return True

    def focus(self):
        if not self.focused:
            self.previous_input_mode = self._game.input.mode
            self._game.input.mode = "typing"
            self.focused = True

    def unfocus(self):
        if self.focused:
            self._game.input.mode = self.previous_input_mode
            self.focused = False

    def update(self, delta_time: float):
        if self.focused:
            new_chars = self._game.input.unload_chars()
            for char in new_chars:
                if char == "backspace":
                    self.font.text = self.font.text[:-1]
                elif self.input_type == "all":
                    self.font.text += char

                if self.input_type in ["int", "float"]:
                    if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        self.font.text += char
                if self.input_type in ["float"]:
                    if char in ["."]:
                        if "." not in self.font.text:
                            self.font.text += char
                if self.input_type in ["lower"]:
                    if char in [
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                        "m",
                        "n",
                        "o",
                        "p",
                        "q",
                        "r",
                        "s",
                        "t",
                        "u",
                        "v",
                        "w",
                        "x",
                        "y",
                        "z",
                        "_",
                    ]:
                        self.font.text += char

    def draw(self, surf, offset: pygame.Vector2 = pygame.Vector2(0, 0)):
        base_pos = pygame.Vector2(self.pos.x - offset[0], self.pos.y - offset[1])
        border_r = pygame.Rect(*base_pos, *self.size)
        pygame.draw.rect(surf, self.colour, border_r, width=1)
        self.font.draw(surf)
        text_width = self.font.width
        if self.focused and (self._game.master_clock % 1 > 0.2):
            pygame.draw.line(
                surf,
                self.colour,
                (base_pos.x + self.padding + text_width, base_pos.y + 2),
                (base_pos.x + self.padding + text_width, base_pos.y + self.size.y - 4),
            )

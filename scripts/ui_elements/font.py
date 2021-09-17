from __future__ import annotations


import pygame
from typing import TYPE_CHECKING
from scripts.core.constants import GAP_SIZE
from scripts.core.utility import clip, swap_colour

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union

__all__ = ["Font"]


class Font:
    def __init__(self, path: str, colour: Tuple[int, int, int], text: str, line_width: int = 0,
            pos: Tuple[int, int] = (0, 0)):
        # Load the font image and convert to individual images.
        letters, letter_spacing = self._load_font_img(path, colour)
        self.letters: List[pygame.Surface] = letters
        self.letter_spacing: List[int] = letter_spacing

        # ensure text is a str
        if not isinstance(text, str):
            text = str(text)

        self.text: str = text
        self.line_width: int = line_width
        self.pos: Tuple[int, int] = pos
        self.line_height: int = self.letters[0].get_height() + 5  # +5 as it isnt returning properly
        self.font_order: List[str] = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
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
            ".",
            "-",
            ",",
            ":",
            "+",
            "'",
            "!",
            "?",
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "(",
            ")",
            "/",
            "_",
            "=",
            "\\",
            "[",
            "]",
            "*",
            '"',
            "<",
            ">",
            ";",
            "∞",
        ]
        self._space_width: int = self.letter_spacing[0]
        self._base_spacing: int = 1
        self._line_spacing: int = 2

    @property
    def height(self) -> int:
        return max(self.number_of_lines * (self.line_height + GAP_SIZE) - GAP_SIZE, self.line_height)

    @property
    def width(self) -> int:
        return self.get_text_width(self.text)

    @property
    def number_of_lines(self) -> int:
        """
        Calculate the number of lines the given text will take up, based on the line width.
        """
        line_width = self.line_width
        text = self.text

        num_lines = 1


        if line_width != 0:
            spaces = []
            x = 0
            for i, char in enumerate(text):
                if char == " ":
                    spaces.append((x, i))
                    x += self._space_width + self._base_spacing
                else:
                    x += self.letter_spacing[self.font_order.index(char)] + self._base_spacing
            line_offset = 0
            for i, space in enumerate(spaces):
                if (space[0] - line_offset) > line_width:
                    line_offset += spaces[i - 1][0] - line_offset
                    if i != 0:
                        text = text[: spaces[i - 1][1]] + "\n" + text[spaces[i - 1][1] + 1 :]
                        num_lines += 1

        return num_lines

    def render(self, surface: pygame.Surface):
        text = self.text
        line_width = self.line_width
        pos = self.pos

        x_offset = 0
        y_offset = 0

        # text wrapping; breaks are on spaces. This can cause some render/clipping issues.
        spaces = []
        x = 0
        for i, char in enumerate(text):
            if char == " ":
                spaces.append((x, i))
                x += self._space_width + self._base_spacing
            else:
                x += self.letter_spacing[self.font_order.index(char)] + self._base_spacing
        line_offset = 0
        for i, space in enumerate(spaces):
            if (space[0] - line_offset) > line_width:
                line_offset += spaces[i - 1][0] - line_offset
                if i != 0:
                    text = text[: spaces[i - 1][1]] + "\n" + text[spaces[i - 1][1] + 1:]

        # draw to surface
        for char in text:
            if char not in ["\n", " "]:
                surface.blit(self.letters[self.font_order.index(char)], (pos[0] + x_offset, pos[1] + y_offset))
                x_offset += self.letter_spacing[self.font_order.index(char)] + self._base_spacing
            elif char == " ":
                x_offset += self._space_width + self._base_spacing
            else:
                y_offset += self._line_spacing + self.line_height
                x_offset = 0

    def get_text_width(self, text: str) -> int:
        """
        Get the width of the given text in the font.
        """
        text_width = 0
        for char in text:
            if char in ["\n", " "]:
                text_width += self._space_width + self._base_spacing
            else:
                text_width += self.letter_spacing[self.font_order.index(char)] + self._base_spacing
        return text_width

    @staticmethod
    def _load_font_img(path: str, colour: Tuple[int, int, int]) -> Tuple[List[pygame.Surface], List[int]]:
        fg_color = (255, 0, 0)
        bg_color = (0, 0, 0)
        font_img = pygame.image.load(path).convert()
        font_img = swap_colour(font_img, fg_color, colour)
        last_x = 0
        letters = []
        letter_spacing = []
        for x in range(font_img.get_width()):
            if font_img.get_at((x, 0))[0] == 127:
                letters.append(clip(font_img, last_x, 0, x - last_x, font_img.get_height()))
                letter_spacing.append(x - last_x)
                last_x = x + 1
            x += 1
        for letter in letters:
            letter.set_colorkey(bg_color)
        return letters, letter_spacing

from __future__ import annotations
import pygame

from typing import TYPE_CHECKING

from scripts.core.constants import ASSET_PATH, FontEffects
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import Dict, Tuple, List, Optional


__all__ = ["FancyFont"]


class FancyFont:
    """
    A font with effects.
    Use '<![font_name]>' in the text to indicate which font to use for the following characters. Fonts names are
    'small', 'big' or 'red'. e.g. text='this is <!red> red'.
    New lines are indicated with '\\n'.
    """

    def __init__(self, text: str, pos: Tuple[int, int], max_width: int = 0,
            font_effects: Optional[List[FontEffects]] = None):

        # handle mutable default
        if font_effects is None:
            font_effects = []

        self.fonts: List[Font] = self._create_fonts()

        # transform text and identify where to swap fonts.
        text, font_swap_markers = self._parse_text(text)

        self.text = text
        self.pos: Tuple[int, int] = pos
        self.font = self.fonts[0]

        self.line_gap = 1  # relative to base font height
        self.character_gap = 1
        self.space_gap = int(self.font.letter_spacing[0] // 3 + 1)
        self.max_width = max_width
        self.used_width = 0

        self.base_characters = [Character(char, self.font, self, index=i) for i, char in enumerate(self.text)]
        self._generate_characters()
        self.characters = [[]]

        self.visible_range = [0, self.length]
        self._initial_start_char_index = 0  # can be set to negative to create a delay when being removed.
        self.start_char_index = self._initial_start_char_index
        self.end_char_index = 0

        # effect flags
        self._fade_in = True
        self._fade_out = False

        for i in range(len(font_swap_markers)):
            start = font_swap_markers[i][0]
            font = font_swap_markers[i][1]
            end = len(text) + 1
            if i < len(font_swap_markers) - 1:
                end = font_swap_markers[i + 1][0]
            self._adjust_font(start, end, font)

    def update(self, delta_time: float):
        # set visible range, determining what chars are shown
        self.visible_range = [int(self.start_char_index), self.end_char_index]

        # increment char indices
        start_increment = 0.5  # N.B. make sure it is slower than the incrementing of
        end_increment = 1

        # if not fading in then we dont need to change the start index
        if self._fade_out:
            self.start_char_index += start_increment

        if self._fade_in:
            self.end_char_index += end_increment
            if self.start_char_index > self.length + 30:
                self.start_char_index = 0
                self.end_char_index = 0

            j = self.end_char_index
            # scale to full size
            self._adjust_scale(j - 20, j - 16, 1)
            self._adjust_scale(j - 12, j, 0.8)

            # fade text in
            self._adjust_alpha(j - 20, j - 16, 255)
            self._adjust_alpha(j - 16, j - 8, 100)
            self._adjust_alpha(j - 8, j, 40)

        else:
            self.end_char_index = self.length

    def render(self, surface: pygame.Surface, offset=(0, 0)):
        x_offset = 0
        y_offset = 0
        for line in self.characters:
            for char in line:
                if (self.visible_range[0] <= char.index < self.visible_range[1]) or (char.index == -1):
                    char.render(surface, (offset[0] + x_offset, offset[1] + y_offset))
                x_offset += char.width
            y_offset += self.font.line_height + self.line_gap
            x_offset = 0

    def _adjust_font(self, start_index: int, end_index: int, new_font: Font):
        """
        Adjust the font of the characters between 2 indices.
        """
        start_index = max(0, start_index)
        for char in self.base_characters[start_index:end_index]:
            char.font = new_font
            char.update()
        self._generate_characters()

    def _adjust_alpha(self, start_index: int, end_index: int, new_alpha: int):
        """
        Adjust the alpha of the characters between 2 indices. new_alpha can be between 0 and 255.
        """
        start_index = max(0, start_index)
        for char in self.base_characters[start_index:end_index]:
            char.alpha = new_alpha
            char.update()
        self._generate_characters()

    def _adjust_scale(self, start_index, end_index, new_scale):
        """
        Adjust the scale of the characters between 2 indices.
        """
        start_index = max(0, start_index)
        for char in self.base_characters[start_index:end_index]:
            char.scale = new_scale
            char.update()
        self._generate_characters()

    @property
    def length(self) -> int:
        return sum([len(line) for line in self.characters])

    @property
    def height(self) -> int:
        return len(self.characters) * (self.font.line_height + self.line_gap) - self.line_gap

    def width(self, characters) -> int:
        return sum([char.width for char in characters])

    def _generate_characters(self):
        """
        Convert the text into Characters.
        """
        word = []
        self.characters = [[]]
        self.used_width = 0

        current_line_width = 0
        for char in self.base_characters:
            add_space = False
            if char.character != "\n":
                word.append(char)
            if char.character in [" ", "\n"]:
                width = self.width(word)
                if self.max_width and (current_line_width + width > self.max_width):  # new line
                    self.characters.append([])
                    self.used_width = max(self.used_width, current_line_width)
                    current_line_width = 0
                else:
                    add_space = True
                self.characters[-1] += word
                current_line_width += width
                if add_space:
                    font = self.font
                    if len(self.characters[-1]):
                        font = self.characters[-1][-1].font
                    new_space = Character(" ", font, self)
                    self.characters[-1].append(new_space)
                    current_line_width += new_space.width
                word = []
            if char.character == "\n":  # new line
                self.characters[-1] += word
                word = []
                self.characters.append([])
                current_line_width = 0

        if word:
            self.characters[-1] += word
            width = self.width(word)
            current_line_width += width

        self.used_width = max(self.used_width, current_line_width)

    @staticmethod
    def _create_fonts() -> List[Font]:
        default_font = Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 255, 255))
        big_font = Font(str(ASSET_PATH / "fonts/large_font.png"), (255, 255, 255))
        red_font = Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0))

        fonts = [default_font, big_font, red_font]
        return fonts

    def _parse_text(self, text: str) -> Tuple[str, List[Tuple[int, Font]]]:
        """
        Parse the text, extracting values from tags, and returns a transformed text and the font swap markers.
        Returns as (updated_text, ([font_swap_markers], Font). font_swap_markers are the indices of where the font
        changes.
        """
        font_swap_markers = []
        tag = ""
        last_start = 0
        text_copy = text
        for i, char in enumerate(text_copy):
            if (tag == "") and (char == "<"):
                last_start = text.find("<!")
                tag = "<"
            if (tag == "<") and (char == "!"):
                tag = "<!"
            elif len(tag) > 1:
                tag += char
                if char == ">":
                    tag_value = tag[2:-1]

                    if tag_value == "red":
                        tag_index = 2
                    elif tag_value == "big":
                        tag_index = 1
                    else:
                        # if tag_value == "small"
                        tag_index = 0

                    font_swap_markers.append((last_start, self.fonts[tag_index]))
                    pos = text.find(tag)
                    text = text[:pos] + text[pos + len(tag):]
                    tag = ""

        return text, font_swap_markers


class Character:
    def __init__(self, character, font, owning_block, index=-1):
        self.index = index
        self.character = character
        self.font = font
        self.alpha = 255
        self.scale = 1
        self.owning_block = owning_block
        self.update()

    def update(self):
        self.width = self.get_width()

    def __str__(self):
        return "<char: " + self.character + ">"

    def __repr__(self):
        return "<char: " + self.character + ">"

    def render(self, surf, offset=(0, 0)):
        if self.character not in ["\n", " "]:
            img = self.font.letters[self.font.font_order.index(self.character)]
            if self.alpha != 255:
                img = img.copy()
                img.set_alpha(self.alpha)
            if self.scale != 1:
                dimensions = (int(img.get_width() * self.scale), int(img.get_height() * self.scale))
                if not (dimensions[0] and dimensions[1]):
                    return
                img = pygame.transform.scale(img, dimensions)
            vertical_shift = int((img.get_height() - self.owning_block.font.line_height) / 2)
            surf.blit(img, (offset[0], offset[1] - vertical_shift))

    def get_width(self):
        if self.character == "\n":
            return 1
        if self.character != " ":
            return int(
                (self.font.letter_spacing[self.font.font_order.index(self.character)] + self.owning_block.character_gap)
                * self.scale
            )
        else:
            return int(self.owning_block.space_gap * self.scale)

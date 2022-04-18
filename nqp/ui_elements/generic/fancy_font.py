from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import ASSET_PATH, FontEffects, TEXT_FADE_IN_SPEED, TEXT_FADE_OUT_SPEED
from nqp.ui_elements.generic.font import Font

if TYPE_CHECKING:
    from typing import List, Optional, Tuple


__all__ = ["FancyFont"]


class FancyFont:
    """
    A font with effects.
    Use '<![font_name]>' in the text to indicate which font to use for the following characters. Fonts names are
    'small', 'big' or 'red'. e.g. text='this is <!red> red'.
    New lines are indicated with '\\n'.
    """

    def __init__(
        self, text: str, pos: pygame.Vector2, line_width: int = 0, font_effects: Optional[List[FontEffects]] = None
    ):

        # handle mutable default
        if font_effects is None:
            font_effects = []

        # ensure text is a str
        if not isinstance(text, str):
            text = str(text)

        self.raw_text: str = text

        self._fonts: List[Font] = self._create_fonts()

        # transform text and identify where to swap _fonts.
        parsed_text, font_swap_markers = self._parse_text(text)

        self._parsed_text: str = parsed_text
        self.pos: pygame.Vector2 = pos
        self.font: Font = self._fonts[0]

        self.line_height: int = self.font.line_height
        self._line_gap: int = 5  # relative to base font height
        self.character_gap: int = 1
        self.space_gap: int = int(self.font.letter_spacing[0] // 3 + 1)
        self.line_width: int = line_width
        self._used_width: int = 0

        self._characters: List[List[Character]] = [[]]
        self._base_characters: List[Character] = self._create_base_characters()
        self._generate_characters()

        self._visible_range = [0, self.length]
        self._initial_start_char_index = 0  # can be set to negative to create a delay when being removed.
        self._start_char_index = self._initial_start_char_index
        self._end_char_index = 0

        # effect flags
        self._fade_in = False
        self._fade_out = False
        self._process_effect_flags(font_effects)

        # utilise font_swap_markers
        self._initial_font_adjustments(parsed_text, font_swap_markers)

    @property
    def length(self) -> int:
        return sum([len(line) for line in self._characters])

    @property
    def height(self) -> int:
        # + 1 to add an extra line at the end to ensure it isnt clipped
        return ((len(self._characters) + 1) * (self.font.line_height + self._line_gap)) - self._line_gap

    @property
    def width(self) -> int:
        return self.get_character_width(self._characters[0])

    def update(self, delta_time: float):
        # set visible range, determining what chars are shown
        self._visible_range = [int(self._start_char_index), self._end_char_index]

        # increment char indices
        start_increment = TEXT_FADE_OUT_SPEED
        end_increment = TEXT_FADE_IN_SPEED

        # if not fading in then we dont need to change the start index
        if self._fade_out:
            self._start_char_index += start_increment

        if self._fade_in:
            self._end_char_index += end_increment
            if self._start_char_index > self.length + 30:
                self._start_char_index = 0
                self._end_char_index = 0

            j = self._end_char_index
            # scale to full size
            self._adjust_scale(j - 20, j - 16, 1)
            self._adjust_scale(j - 12, j, 0.8)

            # fade text in
            self._adjust_alpha(j - 20, j - 16, 255)
            self._adjust_alpha(j - 16, j - 8, 100)
            self._adjust_alpha(j - 8, j, 40)

        else:
            self._end_char_index = self.length

    def draw(self, surface: pygame.Surface):
        if isinstance(self.pos, tuple):
            breakpoint()

        start_x = self.pos.x
        start_y = self.pos.y
        x_offset = 0
        y_offset = 0
        for line in self._characters:
            for char in line:
                if (self._visible_range[0] <= char.index < self._visible_range[1]) or (char.index == -1):
                    char.draw(surface, (start_x + x_offset, start_y + y_offset))
                x_offset += char.width
            y_offset += self.line_height + self._line_gap
            x_offset = 0

    def refresh(self):
        """
        Refresh the font, restarting from the beginning with the current text.
        """
        self._fonts: List[Font] = self._create_fonts()

        # transform text and identify where to swap _fonts.
        parsed_text, font_swap_markers = self._parse_text(self.raw_text)

        self._parsed_text = parsed_text
        self.font = self._fonts[0]

        self.line_height = self.font.line_height
        self._line_gap = 1  # relative to base font height
        self.character_gap = 1
        self.space_gap = int(self.font.letter_spacing[0] // 3 + 1)
        self._used_width = 0

        self._characters: List[List[Character]] = [[]]
        self._base_characters = self._create_base_characters()
        self._generate_characters()

        self._visible_range = [0, self.length]
        self._initial_start_char_index = 0  # can be set to negative to create a delay when being removed.
        self._start_char_index = self._initial_start_char_index
        self._end_char_index = 0

        # utilise font_swap_markers
        self._initial_font_adjustments(parsed_text, font_swap_markers)

    @staticmethod
    def get_character_width(characters: List[Character]) -> int:
        return sum([char.width for char in characters])

    def _initial_font_adjustments(self, parsed_text: str, font_swap_markers):
        """
        Apply the initial font adjustments based on the text returned from _parse_text.
        """
        # utilise font_swap_markers
        for i in range(len(font_swap_markers)):
            start = font_swap_markers[i][0]
            font = font_swap_markers[i][1]
            end = len(parsed_text) + 1
            if i < len(font_swap_markers) - 1:
                end = font_swap_markers[i + 1][0]
            self._adjust_font(start, end, font)

    def _adjust_font(self, start_index: int, end_index: int, new_font: Font):
        """
        Adjust the font of the characters between 2 indices.
        """
        start_index = max(0, start_index)
        for char in self._base_characters[start_index:end_index]:
            char.font = new_font
            char.update()
        self._generate_characters()

    def _adjust_alpha(self, start_index: int, end_index: int, new_alpha: int):
        """
        Adjust the alpha of the characters between 2 indices. new_alpha can be between 0 and 255.
        """
        start_index = max(0, start_index)
        for char in self._base_characters[start_index:end_index]:
            char.alpha = new_alpha
            char.update()
        self._generate_characters()

    def _adjust_scale(self, start_index: int, end_index: int, new_scale: float):
        """
        Adjust the scale of the characters between 2 indices.
        """
        start_index = max(0, start_index)
        for char in self._base_characters[start_index:end_index]:
            char.scale = new_scale
            char.update()
        self._generate_characters()

    def _generate_characters(self):
        """
        Convert the text into Characters. Update _used_width and the character list.
        """
        word = []
        self._characters = [[]]
        self._used_width = 0

        current_line_width = 0
        for char in self._base_characters:
            add_space = False
            if char.character != "\n":
                word.append(char)
            if char.character in [" ", "\n"]:
                width = self.get_character_width(word)
                if self.line_width and (current_line_width + width > self.line_width):  # new line
                    self._characters.append([])
                    self._used_width = max(self._used_width, current_line_width)
                    current_line_width = 0
                else:
                    add_space = True
                self._characters[-1] += word
                current_line_width += width
                if add_space:
                    font = self.font
                    if len(self._characters[-1]):
                        font = self._characters[-1][-1].font
                    new_space = Character(" ", font, self)
                    self._characters[-1].append(new_space)
                    current_line_width += new_space.width
                word = []
            if char.character == "\n":  # new line
                self._characters[-1] += word
                word = []
                self._characters.append([])
                current_line_width = 0

        if word:
            self._characters[-1] += word
            width = self.get_character_width(word)
            current_line_width += width

        self._used_width = max(self._used_width, current_line_width)

    @staticmethod
    def _create_fonts() -> List[Font]:
        default_font = Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 255, 255), "")
        big_font = Font(str(ASSET_PATH / "fonts/large_font.png"), (255, 255, 255), "")
        red_font = Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0), "")

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

                    font_swap_markers.append((last_start, self._fonts[tag_index]))
                    pos = text.find(tag)
                    text = text[:pos] + text[pos + len(tag) :]
                    tag = ""

        return text, font_swap_markers

    def _process_effect_flags(self, font_effects: List[FontEffects]):
        """
        Update the effect flags based on the FontEffects passed in.
        """
        if FontEffects.FADE_IN in font_effects:
            self._fade_in = True

        if FontEffects.FADE_OUT in font_effects:
            self._fade_out = False

    def _create_base_characters(self) -> List[Character]:
        base_chars = [Character(char, self.font, self, index=i) for i, char in enumerate(self._parsed_text)]
        return base_chars


class Character:
    def __init__(self, character, font, owning_block, index=-1):
        self.index = index
        self.character = character
        self.font = font
        self.alpha = 255
        self.scale = 1
        self.width = 0
        self.owning_block = owning_block
        self.update()

    def update(self):
        self.width = self.get_width()

    def __str__(self):
        return "<char: " + self.character + ">"

    def __repr__(self):
        return "<char: " + self.character + ">"

    def draw(self, surf, offset=(0, 0)):
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

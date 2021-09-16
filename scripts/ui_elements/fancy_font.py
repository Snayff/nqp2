from __future__ import annotations
import pygame

__all__ = ["FancyFont", "Character"]



class FancyFont:
    def __init__(self, text, *fonts, max_width=0):

        # parse the text, pulling out tags and assigning fonts as required
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
                    font_swap_markers.append((last_start, fonts[int(tag_value)]))
                    pos = text.find(tag)
                    text = text[:pos] + text[pos + len(tag) :]
                    tag = ""

        self.text = text
        self.font = fonts[0]

        self.line_gap = 1  # relative to base font height
        self.character_gap = 1
        self.space_gap = int(self.font.letter_spacing[0] // 3 + 1)
        self.max_width = max_width
        self.used_width = 0

        self.base_characters = [Character(char, self.font, self, index=i) for i, char in enumerate(self.text)]
        self.generate_characters()
        self.characters = [[]]

        self.visible_range = [0, self.length]
        self._initial_start_char_index = 0  # can be set to negative to create a delay when being removed.
        self.start_char_index = self._initial_start_char_index
        self.end_char_index = 0

        # effects
        self._fade_in = False
        self._fade_out = True

        for i in range(len(font_swap_markers)):
            start = font_swap_markers[i][0]
            font = font_swap_markers[i][1]
            end = len(text) + 1
            if i < len(font_swap_markers) - 1:
                end = font_swap_markers[i + 1][0]
            self.adjust_font(start, end, font)

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

            # fade text in
            j = self.end_char_index
            self.adjust_scale(j - 20, j - 16, 1)
            self.adjust_scale(j - 12, j, 0.8)
            self.adjust_alpha(j - 20, j - 16, 255)
            self.adjust_alpha(j - 16, j - 8, 100)
            self.adjust_alpha(j - 8, j, 40)

        else:
            self.end_char_index = self.length

    def render(self, surf, offset=(0, 0)):
        x_offset = 0
        y_offset = 0
        for line in self.characters:
            for char in line:
                if (self.visible_range[0] <= char.index < self.visible_range[1]) or (char.index == -1):
                    char.render(surf, (offset[0] + x_offset, offset[1] + y_offset))
                x_offset += char.width
            y_offset += self.font.height + self.line_gap
            x_offset = 0

    def adjust_font(self, start, end, new_font):
        start = max(0, start)
        for char in self.base_characters[start:end]:
            char.font = new_font
            char.update()
        self.generate_characters()

    def adjust_alpha(self, start, end, new_alpha):
        start = max(0, start)
        for char in self.base_characters[start:end]:
            char.alpha = new_alpha
            char.update()
        self.generate_characters()

    def adjust_scale(self, start, end, new_scale):
        start = max(0, start)
        for char in self.base_characters[start:end]:
            char.scale = new_scale
            char.update()
        self.generate_characters()

    @property
    def length(self):
        return sum([len(line) for line in self.characters])

    @property
    def height(self):
        return len(self.characters) * (self.font.height + self.line_gap) - self.line_gap


    def char_width(self, characters) -> int:
        return sum([char.width for char in characters])

    def generate_characters(self):
        word = []
        self.characters = [[]]
        self.used_width = 0
        current_line_width = 0
        for char in self.base_characters:
            add_space = False
            if char.character != "\n":
                word.append(char)
            if char.character in [" ", "\n"]:
                width = self.char_width(word)
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

        if word != []:
            self.characters[-1] += word
            width = self.char_width(word)
            current_line_width += width

        self.used_width = max(self.used_width, current_line_width)


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
            vertical_shift = int((img.get_height() - self.owning_block.font.height) / 2)
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

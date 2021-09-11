import pygame

from scripts.core.utility import clip, swap_color


def load_font_img(path, font_color):
    fg_color = (255, 0, 0)
    bg_color = (0, 0, 0)
    font_img = pygame.image.load(path).convert()
    font_img = swap_color(font_img, fg_color, font_color)
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
    return letters, letter_spacing, font_img.get_height()

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
        return '<char: ' + self.character + '>'

    def __repr__(self):
        return '<char: ' + self.character + '>'

    def render(self, surf, offset=(0, 0)):
        if self.character not in ['\n', ' ']:
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
        if self.character == '\n':
            return 1
        if self.character != ' ':
            return int((self.font.letter_spacing[self.font.font_order.index(self.character)] + self.owning_block.character_gap) * self.scale)
        else:
            return int(self.owning_block.space_gap * self.scale)

# generates a TextBlock from formatted text. <!2> would swap the text following the tag with the 2nd font given. The first font is the default.
def formatted_text_gen(text, *fonts, max_width=0):
    font_swap_markers = []
    tag = ''
    last_start = 0
    text_copy = text
    for i, char in enumerate(text_copy):
        if (tag == '') and (char == '<'):
            last_start = text.find('<!')
            tag = '<'
        if (tag == '<') and (char == '!'):
            tag = '<!'
        elif len(tag) > 1:
            tag += char
            if char == '>':
                tag_value = tag[2:-1]
                font_swap_markers.append((last_start, fonts[int(tag_value)]))
                pos = text.find(tag)
                text = text[:pos] + text[pos + len(tag):]
                tag = ''

    tb = TextBlock(text, fonts[0], max_width=max_width)
    for i in range(len(font_swap_markers)):
        start = font_swap_markers[i][0]
        font = font_swap_markers[i][1]
        end = len(text) + 1
        if i < len(font_swap_markers) - 1:
            end = font_swap_markers[i + 1][0]
        tb.adjust_font(start, end, font)

    return tb

class TextBlock:
    def __init__(self, text, font, max_width=0):
        self.text = text
        self.font = font
        self.line_gap = 1 # relative to base font height
        self.character_gap = 1
        self.space_gap = int(font.letter_spacing[0] // 3 + 1)
        self.max_width = max_width
        self.base_characters = [Character(char, font, self, index=i) for i, char in enumerate(self.text)]
        self.generate_characters()
        self.visible_range = [0, self.length]

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

    def char_width(self, characters):
        return sum([char.width for char in characters])

    def generate_characters(self):
        word = []
        self.characters = [[]]
        self.used_width = 0
        current_line_width = 0
        for char in self.base_characters:
            add_space = False
            if char.character != '\n':
                word.append(char)
            if char.character in [' ', '\n']:
                width = self.char_width(word)
                if self.max_width and (current_line_width + width > self.max_width): # new line
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
                    new_space = Character(' ', font, self)
                    self.characters[-1].append(new_space)
                    current_line_width += new_space.width
                word = []
            if char.character == '\n': # new line
                self.characters[-1] += word
                word = []
                self.characters.append([])
                current_line_width = 0

        if word != []:
            self.characters[-1] += word
            width = self.char_width(word)
            current_line_width += width

        self.used_width = max(self.used_width, current_line_width)

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

class Font:
    def __init__(self, path, colour):
        self.letters, self.letter_spacing, self.line_height = load_font_img(path, colour)
        self.height = self.letters[0].get_height()
        self.font_order = [
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
        self.space_width = self.letter_spacing[0]
        self.base_spacing = 1
        self.line_spacing = 2

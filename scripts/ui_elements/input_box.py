import pygame

class InputBox:
    def __init__(self, game, size, pos=[0, 0], color=(255, 255, 255), input_type='all', text='', font=None):
        self.game = game
        self.size = list(size)
        self.pos = list(pos)
        self.color = color

        if input_type == 'detect':
            if type(text) == int:
                input_type = 'int'
            elif type(text) == float:
                input_type = 'float'
            else:
                input_type = 'lower'

        self.input_type = input_type

        self.text = str(text)
        self.previous_input_mode = None
        self.padding = 3
        self.focused = False

        if not font:
            font = self.game.assets.fonts['default']
        self.font = font

    @property
    def value(self):
        if self.input_type == 'int':
            return int(self.text)
        if self.input_type == 'float':
            return float(self.text)
        else:
            return self.text

    @property
    def should_focus(self, offset=(0, 0)):
        if not self.focused:
            r = pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1])
            if r.collidepoint(self.game.input.mouse_pos):
                if self.game.input.mouse_state['left']:
                    return True

            return False

        else:
            r = pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1])
            if not r.collidepoint(self.game.input.mouse_pos):
                if self.game.input.mouse_state['left']:
                    return False

            return True

    def focus(self):
        if not self.focused:
            self.previous_input_mode = self.game.input.mode
            self.game.input.mode = 'typing'
            self.focused = True

    def unfocus(self):
        if self.focused:
            self.game.input.mode = self.previous_input_mode
            self.focused = False

    def update(self):
        if self.focused:
            new_chars = self.game.input.unload_chars()
            for char in new_chars:
                if char == 'backspace':
                    self.text = self.text[:-1]
                elif self.input_type == 'all':
                    self.text += char

                if self.input_type in ['int', 'float']:
                    if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        self.text += char
                if self.input_type in ['float']:
                    if char in ['.']:
                        if '.' not in self.text:
                            self.text += char
                if self.input_type in ['lower']:
                    if char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '_']:
                        self.text += char

    def render(self, surf, offset=(0, 0)):
        base_pos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        border_r = pygame.Rect(*base_pos, *self.size)
        pygame.draw.rect(surf, self.color, border_r, width=1)
        self.font.render(self.text, surf, (base_pos[0] + self.padding, base_pos[1] + (self.size[1] - self.font.height) // 2))
        text_width = self.font.width(self.text)
        if self.focused and (self.game.master_clock % 1 > 0.2):
            pygame.draw.line(surf, self.color, (base_pos[0] + self.padding + text_width, base_pos[1] + 2), (base_pos[0] + self.padding + text_width, base_pos[1] + self.size[1] - 4))

import pygame

from scripts.core.input_box import InputBox
from scripts.core.button import Button
from scripts.core.base_classes.scene import Scene

class UnitDataScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.left_arrow = Button(game, pygame.transform.flip(self.game.assets.get_image('ui', 'arrow_button'), True, False), (10, 10))
        self.right_arrow = Button(game, self.game.assets.get_image('ui', 'arrow_button'), (120, 10))

        self.save_button = Button(game, 'save', (400, 300), size=[30, 20])

        self.fields = {}

        self.unit_list = list(self.game.data.units)
        self.unit_index = 0
        self.load_unit(self.unit_list[self.unit_index])

    def load_unit(self, unit_id):
        self.current_unit = unit_id
        self.current_unit_data = self.game.data.units[unit_id]
        self.game.input.mode = 'default'

        self.fields = {}
        for i, field in enumerate(self.current_unit_data):
            y = i % 10
            x = i // 10
            self.fields[field] = InputBox(self.game, [80, 16], pos=[100 + x * 200, 30 + y * 20], input_type='detect', text=self.current_unit_data[field])

    def render(self, surf=None):
        if not surf:
            surf = self.game.window.display

        self.game.assets.fonts['default'].render(self.current_unit, surf, (76 - self.game.assets.fonts['default'].width(self.current_unit) // 2, 15))

        for field in self.current_unit_data:
            self.game.assets.fonts['default'].render(field, surf, (self.fields[field].pos[0] - 90, self.fields[field].pos[1] + 3))
            self.fields[field].render(surf)

        for button in [self.left_arrow, self.right_arrow, self.save_button]:
            button.render(surf)

    def update(self):
        for button in [self.left_arrow, self.right_arrow, self.save_button]:
            button.update()
            if button.pressed:
                if button == self.right_arrow:
                    self.unit_index += 1
                    if self.unit_index >= len(self.unit_list):
                        self.unit_index = 0
                if button == self.left_arrow:
                    self.unit_index -= 1
                    if self.unit_index < 0:
                        self.unit_index = len(self.unit_list) - 1
                if button in [self.left_arrow, self.right_arrow]:
                    self.load_unit(self.unit_list[self.unit_index])

                if button == self.save_button:
                    for field in self.current_unit_data:
                        self.current_unit_data[field] = self.fields[field].value
                    # TODO: save to JSON here?
                    print(self.current_unit_data)

        for field in self.current_unit_data:
            self.fields[field].update()
            if self.fields[field].should_focus:
                self.fields[field].focus()
            else:
                self.fields[field].unfocus()

import sys

import pygame

from management.window import Window
from management.input import Input
from screens.combat import Combat

class Game:
    def __init__(self):

        self.window = Window(self)
        self.input = Input(self)
        self.combat = Combat(self)

    def update(self):
        self.input.update()
        self.combat.update()

    def render(self):
        self.window.render_frame()
        self.combat.render()

    def run(self):
        while True:
            self.update()
            self.render()

    def quit(self):
        pygame.quit()
        sys.exit()


Game().run()

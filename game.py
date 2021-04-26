import sys

import pygame

from scripts.management.window import Window
from scripts.management.input import Input
from scripts.management.memory import Memory
from scripts.management.assets import Assets
from scripts.screens.combat import Combat

class Game:
    def __init__(self):

        self.window = Window(self)
        self.input = Input(self)
        self.memory = Memory(self)
        self.combat = Combat(self)
        self.assets = Assets(self)

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

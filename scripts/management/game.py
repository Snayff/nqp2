from __future__ import annotations

from scripts.management.window import Window
from scripts.management.input import Input
from scripts.management.memory import Memory
from scripts.management.assets import Assets
from scripts.misc.constants import GameState
from scripts.screens.combat import Combat

class Game:
    def __init__(self):

        self.window = Window(self)
        self.input = Input(self)
        self.memory = Memory(self)
        self.combat = Combat(self)
        self.assets = Assets(self)

        # point this to whatever "screen" is active
        self.active_screen = self.combat

        self.current_state: GameState = GameState.PLAYING

    def update(self):
        self.input.update()
        self.active_screen.update()

    def render(self):
        self.window.render_frame()
        self.active_screen.render()

    def run(self):
        self.update()
        self.render()

    def quit(self):
        self.current_state = GameState.EXITING




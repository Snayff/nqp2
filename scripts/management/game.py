from __future__ import annotations

from scripts.management.assets import Assets
from scripts.management.input import Input
from scripts.management.memory import Memory
from scripts.management.window import Window
from scripts.misc.constants import GameState
from scripts.screens.combat import Combat
from scripts.screens.overworld import Overworld

__all__ = ["Game"]


class Game:
    def __init__(self):

        # managers
        self.window = Window(self)
        self.input = Input(self)
        self.memory = Memory(self)
        self.assets = Assets(self)

        # screens
        self.combat = Combat(self)
        self.overworld = Overworld(self)

        # point this to whatever "screen" is active
        self.active_screen = self.combat

        self.state: GameState = GameState.PLAYING

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
        self.state = GameState.EXITING

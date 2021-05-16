from __future__ import annotations

from scripts.management.assets import Assets
from scripts.management.input import Input
from scripts.management.memory import Memory
from scripts.management.window import Window
from scripts.misc.constants import GameState
from scripts.scenes.combat import Combat
from scripts.scenes.event import Event
from scripts.scenes.overworld import Overworld

__all__ = ["Game"]


class Game:
    def __init__(self):

        # managers
        self.window = Window(self)
        self.input = Input(self)
        self.memory = Memory(self)
        self.assets = Assets(self)

        # scenes
        self.combat: Combat = Combat(self)
        self.overworld: Overworld = Overworld(self)
        self.event: Event = Event(self)

        # point this to whatever "screen" is active
        self.active_scene = self.overworld

        self.state: GameState = GameState.PLAYING

    def update(self):
        self.input.update()
        self.active_scene.update()

    def render(self):
        self.window.render_frame()
        self.active_scene.render()

    def run(self):
        self.update()
        self.render()

    def quit(self):
        self.state = GameState.EXITING

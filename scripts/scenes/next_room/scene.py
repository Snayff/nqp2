from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.core.debug import Timer
from scripts.scenes.next_room.ui import NextRoomUI

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["NextRoomScene"]


class NextRoomScene(Scene):
    def __init__(self, game: Game):
        with Timer("EventScene initialisation"):
            super().__init__(game, SceneType.EVENT)
            self.ui: NextRoomUI = NextRoomUI(game, self)

    def update(self, delta_time: float):
        self.ui.update(delta_time)

    def reset(self):
        self.ui = NextRoomUI(self._game, self)

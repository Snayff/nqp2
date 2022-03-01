from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import EventState
from scripts.core.debug import Timer


if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["EventController"]


class EventController(Controller):
    """
    Event game functionality and event-only data.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("EventController initialised"):
            super().__init__(game, parent_scene)

            self.state: EventState = EventState.IDLE


    def update(self, delta_time: float):
        pass

    def reset(self):
        pass



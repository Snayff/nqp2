from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.event.ui import EventUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["EventScene"]


class EventScene(Scene):
    """
    Handles EventScene interactions and consolidates the rendering. EventScene is used to give players a text choice.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: EventUI = EventUI(game)

        self.active_event: Dict = {}

        # record duration
        end_time = time.time()
        logging.info(f"EventScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def reset(self):
        self.ui = EventUI(self.game)

        self.active_event = {}

    def load_random_event(self):
        self.active_event = self.game.memory.get_random_event([self.game.memory.level])

    def trigger_result(self, option_index: int):
        """
        Trigger the result for the indicated option.

        Results are in a key value pair, separated by a colon. Separate results are split  by a comma.
        Example:
            "Gold:10,Gold:10" - would add 10 gold twice.
        """
        result_string = self.active_event["options"][option_index]["result"]
        result_list = result_string.split(",")

        for result_line in result_list:
            key, value = result_line.split(":", 1)
            self._action_result(key, value)

    def _action_result(self, result_key: str, result_value: str):
        """
        Resolve the action from the result
        """
        if result_key == "gold":
            original_value = self.game.memory.gold
            self.game.memory.amend_gold(int(result_value))
            logging.info(f"Gold changed by {result_value};  {original_value} -> {self.game.memory.gold}.")

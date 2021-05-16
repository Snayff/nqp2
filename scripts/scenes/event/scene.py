from __future__ import annotations

import random
from typing import TYPE_CHECKING

from scripts.scenes.event.ui import EventUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["Event"]


class Event:
    """
    Handles Event interactions and consolidates the rendering. Event is used to give players a text choice.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: EventUI = EventUI(game)

        self.active_event: Dict = self._get_random_event()

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def _get_random_event(self) -> Dict:
        if len(self.game.memory.events) > 0:

            # convert dict items to list, get a random choice from list, get the dict value from the tuple
            event = random.choice(list(self.game.memory.events.items()))[1]
        else:
            event = {}
        return event

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
            self._amend_gold(int(result_value))

    def _amend_gold(self, amount: int):
        """
        Amend the current gold value by the given amount.
        """
        self.game.memory.gold = max(0, self.game.memory.gold + amount)

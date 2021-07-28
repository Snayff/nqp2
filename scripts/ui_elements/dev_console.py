from __future__ import annotations

import logging

from scripts.core.constants import SceneType
from scripts.ui_elements.input_box import InputBox

__all__ = ["DevConsole"]



class DevConsole(InputBox):
    def __init__(self, game):
        size = (100, 30)
        pos = (10, 10)
        super().__init__(game, size, pos)

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.focused:

            # pressed enter
            if self.game.input.states["typing_enter"]:
                self.handle_dev_command()

    def handle_dev_command(self):
        """
        Handle the command in the dev console. Expected format is "[command] [value]".
        """
        command = self.text

        if command[:5] == "event":
            event_id = command[6:]  # +1 position to account for space

            # validate event
            if event_id in self.game.memory.event_deck.keys():
                # load event
                self.game.event.load_event(event_id)
                self.game.event.ui.rebuild_ui()
                self.game.active_scene = self.game.event

            else:
                logging.warning(f"DevConsole: {event_id} not found.")




from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from nqp.core.debug import Timer

if TYPE_CHECKING:
    from typing import List

    from nqp.command.troupe import Troupe
    from nqp.core.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “scenes”. E.g. achievements.
    """

    def __init__(self, game: Game):
        with Timer("Memory: initialised"):

            self._game: Game = game

            self.flags: List[str] = []  # event, game or other flags to note key happenings
            # TODO  - do we need to distinguish between in-run flags and permanent ones?
            self._last_id: int = 0

    def initialise_run(self, troupe: Troupe, gold: int, rations: int, morale: int, charisma: int, leadership: int):
        """
        Initialise the run's values.
        """
        if self._game.world is None:
            logging.error(f"Tried to initialise a run but WorldScene doesnt exist.")
            raise Exception

        self._game.world.model.reset()

        self._game.world.model.add_troupe(troupe)
        self._game.world.model.amend_gold(gold)
        self._game.world.model.amend_rations(rations)
        self._game.world.model.amend_morale(morale)
        self._game.world.model.amend_charisma(charisma)
        self._game.world.model.amend_leadership(leadership)

    def generate_id(self) -> int:
        """
        Create unique ID for an instance, such as a unit.
        """
        self._last_id += 1
        return self._last_id

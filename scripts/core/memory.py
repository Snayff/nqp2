from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from scripts.core.debug import Timer


if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.scene_elements.troupe import Troupe
    from scripts.core.game import Game

__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “scenes”. E.g. achievements.
    """

    def __init__(self, game: Game):
        with Timer("WorldModel initialised"):

            self._game: Game = game

            self.flags: List[str] = []  # event, game or other flags to note key happenings



    def initialise_run(self, troupe: Troupe, gold: int, rations: int, morale: int, charisma: int, leadership: int):
        """
        Initialise the run's values.
        """
        if self._game.world is None:
            logging.error(f"Tried to initialise a run but WorldScene doesnt exist.")
            raise Exception

        self._game.world.model.add_troupe(troupe)
        self._game.world.model.amend_gold(gold)
        self._game.world.model.amend_rations(rations)
        self._game.world.model.amend_morale(morale)
        self._game.world.model.amend_charisma(charisma)
        self._game.world.model.amend_leadership(leadership)

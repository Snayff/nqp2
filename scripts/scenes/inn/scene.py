from __future__ import annotations

import logging
import random
import time
from typing import List, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.inn.ui import InnUI

if TYPE_CHECKING:
    from typing import Dict

    from scripts.core.game import Game

__all__ = ["InnScene"]


class InnScene(Scene):
    """
    Handles InnScene interactions and consolidates the rendering. InnScene is used to buy units.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: InnUI = InnUI(game)

        self.units_for_sale: Troupe = Troupe(self.game, "inn")

        # record duration
        end_time = time.time()
        logging.info(f"InnScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def purchase_unit(self, option_index: int):
        """
        Purchase the unit
        """
        unit = option_index  # FIXME - get the unit using the option index

        # can we afford
        if unit.gold_cost <= self.game.memory.gold:
            # pay gold
            self.game.memory.amend_gold(-unit.gold_cost)  # remove gold cost

            # add unit
            self.game.memory.player_troupe.add_unit(unit)

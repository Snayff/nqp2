from __future__ import annotations

import logging
import random
import time
from typing import List, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.combat.elements.unit import Unit
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

        player_troupe = self.game.memory.player_troupe
        self.sale_troupe: Troupe = Troupe(self.game, "inn", player_troupe.allies)

        # record duration
        end_time = time.time()
        logging.info(f"InnScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)

    def render(self):
        self.ui.render(self.game.window.display)

    def purchase_unit(self, unit: Unit):
        """
        Purchase the unit
        """

        # pay gold
        self.game.memory.amend_gold(-unit.gold_cost)  # remove gold cost

        # add unit
        self.game.memory.player_troupe.add_unit(unit)

        # remove option from list
        self.sale_troupe.remove_unit(unit.id)

    def generate_sale_options(self):
        """
        Generate the options for sale at the Inn.
        """
        # update troupe to match players
        player_troupe = self.game.memory.player_troupe
        self.sale_troupe.allies = player_troupe.allies

        self.sale_troupe.remove_all_units()
        self.sale_troupe.generate_units(5)

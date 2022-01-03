from __future__ import annotations

import logging
import random
import time
from typing import List, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import SceneType
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.combat.elements.unit import Unit
from scripts.scenes.inn.ui import InnUI

if TYPE_CHECKING:
    from typing import Dict, Optional

    from scripts.core.game import Game

__all__ = ["InnScene"]


class InnScene(Scene):
    """
    Handles InnScene interactions and consolidates the rendering. InnScene is used to buy units.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game, SceneType.TRAINING)

        self.ui: InnUI = InnUI(game, self)

        self.sale_troupe: Optional[Troupe] = None
        self.units_available: Dict[int, bool] = {}  # unit.id : is available

        # record duration
        end_time = time.time()
        logging.debug(f"InnScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        super().update(delta_time)
        self.ui.update(delta_time)


    def reset(self):
        self.ui = InnUI(self.game, self)

        self.sale_troupe = None

    def purchase_unit(self, unit: Unit):
        """
        Purchase the unit
        """

        # pay gold
        self.game.memory.amend_gold(-unit.gold_cost)  # remove gold cost

        # add unit
        self.game.memory.player_troupe.add_unit(unit)

        # update unit availability
        self.units_available[unit.id] = False

    def generate_sale_options(self):
        """
        Generate the options for sale at the Inn.
        """
        # update troupe to match players
        player_troupe = self.game.memory.player_troupe
        self.sale_troupe = Troupe(self.game, "inn", player_troupe.allies)

        self.sale_troupe.generate_units(5)

        # add to available
        for unit in self.sale_troupe.units.values():
            self.units_available[unit.id] = True

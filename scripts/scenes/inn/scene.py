from __future__ import annotations

import random
from typing import List, TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
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
        super().__init__(game)

        self.ui: InnUI = InnUI(game)

        self.units_for_sale: List = self._get_random_units(5)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def _get_random_units(self, number_of_units: int) -> List:
        units = []
        max_attempts = 100

        if len(self.game.memory.units) > 0:

            for i in range(0, number_of_units - 1):
                unique = False
                attempts = 0
                unit = {}

                while not unique:
                    # convert dict items to list, get a random choice from list, get the dict value from the tuple
                    choice = random.choice(list(self.game.memory.units.items()))
                    unit[choice[0]] = choice[1]

                    # ensure we havent pulled a unit already on offer, or have reached max attempts
                    if unit not in units or attempts == max_attempts:
                        unique = True
                    else:
                        unit = {}

                    # increment
                    attempts += 1

                # add to units
                units.append(unit)

        return units

    def purchase_unit(self, option_index: int):
        """
        Purchase the unit
        """

        name = list(self.units_for_sale[option_index])[0]
        details = self.units_for_sale[option_index].get(name)

        # can we afford
        if details["gold_cost"] <= self.game.memory.gold:
            # pay gold
            self.game.memory.amend_gold(-details["gold_cost"])

            # add unit
            self.game.memory.amend_unit(name)

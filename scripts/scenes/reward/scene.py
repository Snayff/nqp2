from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.combat.elements.unit import Unit
from scripts.scenes.reward.ui import RewardUI

if TYPE_CHECKING:
    from scripts.core.game import Game
    from typing import List

__all__ = ["RewardScene"]


class RewardScene(Scene):
    """
    Handles RewardScene interactions and consolidates the rendering. RewardScene is used to provide a choice of
    rewards for the player to pick from.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__(game)

        self.ui: RewardUI = RewardUI(game)

        self.reward_units: Troupe = Troupe(self.game, "reward")
        self.gold_reward: int = 0

        # record duration
        end_time = time.time()
        logging.info(f"RewardScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def generate_reward(self):
        """
        Generate reward to offer.
        """
        num_rewards = 3
        gold_min = 10
        gold_max = 50

        # roll gold
        self.gold_reward = random.randint(gold_min, gold_max)

        # generate units in Troupe
        self.reward_units.remove_all_units()
        self.reward_units.generate_units(num_rewards)

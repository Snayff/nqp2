from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from scripts.core.base_classes.scene import Scene
from scripts.core.constants import RewardType
from scripts.scenes.combat.elements.troupe import Troupe
from scripts.scenes.combat.elements.unit import Unit
from scripts.scenes.reward.ui import RewardUI

if TYPE_CHECKING:
    from typing import Any, List

    from scripts.core.game import Game

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

        # reward management
        self.current_rewards = None  # holds the current rewards, e.g. troupe_rewards
        self.reward_type: RewardType = RewardType.UNIT
        self.num_rewards: int = 3

        # reward options
        self.gold_reward: int = 0
        self.troupe_rewards: Troupe = Troupe(self.game, "reward")
        self.resource_rewards = None
        self.upgrade_rewards = None
        self.action_rewards = None

        # record duration
        end_time = time.time()
        logging.info(f"RewardScene: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)

    def generate_reward(self):
        """
        Generate reward to offer. Overwrites existing rewards.
        """
        gold_min = 10
        gold_max = 50

        # roll gold
        self.gold_reward = self.game.rng.randint(gold_min, gold_max)

        # generate required rewards
        reward_type = self.reward_type
        if reward_type == RewardType.UNIT:
            self._generate_troupe_rewards()
            current_reward = self.troupe_rewards

        elif reward_type == RewardType.ACTION:
            self._generate_action_rewards()
            current_reward = self.action_rewards

        elif reward_type == RewardType.UPGRADE:
            self._generate_upgrade_rewards()
            current_reward = self.upgrade_rewards

        else:
            # reward_type == RewardType.RESOURCE
            current_reward = self.resource_rewards
            self._generate_resource_rewards()

        # update current rewards
        self.current_rewards = current_reward

    def _generate_troupe_rewards(self):

        # generate units in Troupe
        self.troupe_rewards.remove_all_units()
        self.troupe_rewards.generate_units(self.num_rewards)

    def _generate_action_rewards(self):
        """STUB"""
        pass

    def _generate_upgrade_rewards(self):
        """STUB"""
        pass

    def _generate_resource_rewards(self):
        """STUB"""
        pass

    def choose_reward(self, reward: Any):
        """
        Add the current reward and the reward gold.
        """
        # add current reward
        reward_type = self.reward_type
        if reward_type == RewardType.UNIT:
            self._choose_troupe_rewards(reward)

        elif reward_type == RewardType.ACTION:
            self._choose_action_rewards(reward)

        elif reward_type == RewardType.UPGRADE:
            self._choose_upgrade_rewards(reward)

        else:
            # reward_type == RewardType.RESOURCE
            self._choose_resource_rewards(reward)

        # add gold
        self.game.memory.amend_gold(self.gold_reward)

    def _choose_troupe_rewards(self, reward: Unit):
        if isinstance(reward, Unit):
            self.game.memory.player_troupe.add_unit(reward)
        else:
            logging.warning(
                f"Chose {reward} as a unit reward. As it isnt a unit, something has "
                f"seriously gone wrong! No reward added."
            )

    def _choose_action_rewards(self, reward: Any):
        """STUB"""
        pass

    def _choose_upgrade_rewards(self, reward: Any):
        """STUB"""
        pass

    def _choose_resource_rewards(self, reward: Any):
        """STUB"""
        pass
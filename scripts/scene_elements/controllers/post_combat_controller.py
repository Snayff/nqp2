from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from scripts.core.base_classes.controller import Controller
from scripts.core.constants import PostCombatState, RewardType
from scripts.core.debug import Timer
from scripts.scene_elements.troupe import Troupe
from scripts.scene_elements.unit import Unit

if TYPE_CHECKING:
    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene

__all__ = ["PostCombatController"]


class PostCombatController(Controller):
    """
    Handles RewardScene interactions

    RewardScene is used to provide a choice of rewards for the player
    to pick from.

    * Modify game state in accordance with game rules
    * Do not draw anything

    """
    def __init__(self, game: Game, parent_scene: WorldScene):
        with Timer("PostCombatController initialised"):
            super().__init__(game, parent_scene)
            self.state: PostCombatState = PostCombatState.VICTORY

            # reward management
            # holds the current rewards, e.g. troupe_rewards
            self.current_rewards = None
            self.reward_type: RewardType = RewardType.UNIT
            self.num_rewards: int = 3

            # reward options
            self.gold_reward: int = 0
            self.troupe_rewards: Optional[Troupe] = None
            self.resource_rewards = None
            self.upgrade_rewards = None
            self.action_rewards = None

    def update(self, delta_time: float):
        pass

    def reset(self):
        self.state = PostCombatState.VICTORY

        # reward management
        # holds the current rewards, e.g. troupe_rewards
        self.current_rewards = None
        self.reward_type = RewardType.UNIT
        self.num_rewards = 3

        # reward options
        self.gold_reward = 0
        player_troupe = self._game.memory.player_troupe
        self.troupe_rewards = Troupe(self._game, "reward", player_troupe.allies)
        self.resource_rewards = None
        self.upgrade_rewards = None
        self.action_rewards = None

    def generate_reward(self):
        """
        Generate reward to offer. Overwrites existing rewards.

        """
        gold_min = self._game.data.config["post_combat"]["gold_min"]
        gold_max = self._game.data.config["post_combat"]["gold_max"]
        gold_level_multiplier = self._game.data.config["post_combat"]["gold_level_multiplier"]
        level = self._game.memory.level

        # only apply multiplier after level 1
        if level > 1:
            mod = level * gold_level_multiplier
        else:
            mod = 1

        # roll gold
        self.gold_reward = int(self._game.rng.randint(gold_min, gold_max) * mod)

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
        # update troupe to match players
        player_troupe = self._game.memory.player_troupe
        self.troupe_rewards.allies = player_troupe.allies

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
        self._game.memory.amend_gold(self.gold_reward)

    def _choose_troupe_rewards(self, reward: Unit):
        if isinstance(reward, Unit):
            # check can afford
            has_enough_charisma = self._game.memory.commander.charisma_remaining > 0
            if has_enough_charisma:
                self._game.memory.player_troupe.add_unit(reward)
        else:
            logging.error(
                f"Chose {reward} as a unit reward. As it isn't a unit, something has "
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

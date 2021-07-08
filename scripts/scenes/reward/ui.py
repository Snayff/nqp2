from __future__ import annotations

import logging
from typing import Optional, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, RewardType, SceneType
from scripts.scenes.combat.elements.unit import Unit

if TYPE_CHECKING:
    from scripts.core.game import Game

__all__ = ["RewardUI"]


class RewardUI(UI):
    """
    Represent the UI of the RewardScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_reward: Optional[Unit] = None

        self.set_instruction_text("Choose your rewards.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # get index value depending on reward
        reward_type = self.game.reward.reward_type
        reward = self.game.reward
        if reward_type == RewardType.UNIT:
            index_size = len(reward.troupe_rewards.units)
        elif reward_type == RewardType.ACTION:
            index_size = 0
        elif reward_type == RewardType.UPGRADE:
            index_size = 0
        else:
            # reward_type == RewardType.RESOURCE
            index_size = 0

        self.set_element_array_dimensions(1, index_size)
        self.handle_directional_input_for_selection()
        self.handle_selector_index_looping()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            if self.selected_reward:
                self.game.reward.choose_reward(self.selected_reward)
                self.game.change_scene(SceneType.OVERWORLD)

        # exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.surface):
        reward_type = self.game.reward.reward_type
        if reward_type == RewardType.UNIT:
            self._render_unit_rewards(surface)

        elif reward_type == RewardType.ACTION:
            pass

        elif reward_type == RewardType.UPGRADE:
            pass

        else:
            # reward_type == RewardType.RESOURCE
            pass

        # show core info
        self.draw_gold(surface)
        self.draw_charisma(surface)
        self.draw_leadership(surface)
        self.draw_instruction(surface)

    def _render_unit_rewards(self, surface: pygame.surface):

        reward_units = list(self.game.reward.troupe_rewards.units.values())
        default_font = self.default_font
        disabled_font = self.disabled_font
        warning_font = self.warning_font
        positive_font = self.positive_font
        stats = ["type", "health", "defence", "attack", "range", "attack_speed", "move_speed", "ammo", "count"]

        # positions
        start_x = 20
        start_y = 60
        gap = 10
        font_height = 12
        window_width = self.game.window.width
        window_height = self.game.window.height
        col_width = int((window_width - (start_x * 2)) / len(stats))

        # victory message
        positive_font.render("Victory!", surface, (start_x, start_y))

        # gold reward
        current_y = start_y + (font_height * 2)
        gold_reward = self.game.reward.gold_reward
        default_font.render(f"{gold_reward} gold scavenged from the dead.", surface, (start_x, current_y))

        # instruction
        current_y = window_height // 2
        warning_font.render(f"Choose one of the following rewards.", surface, (start_x, current_y))

        # draw headers
        current_y = current_y + (font_height * 2)
        col_count = 0
        for stat in stats:
            col_x = start_x + (col_width * col_count)
            default_font.render(stat, surface, (col_x, current_y))

            col_count += 1

        # draw unit info
        row_count = 0
        for unit in reward_units:
            active_font = default_font

            option_y = current_y + ((font_height + gap) * (row_count + 1))  # + 1 due to headers

            # draw stats
            col_count = 0
            for stat in stats:
                col_x = start_x + (col_width * col_count)

                text = str(getattr(unit, stat))
                active_font.render(text, surface, (col_x, option_y))

                col_count += 1

            # draw selector
            if row_count == self.selected_row:
                # note the selected unit
                self.selected_reward = unit

                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, option_y + font_height),
                    (start_x + active_font.width(unit.type), option_y + font_height),
                )

            row_count += 1

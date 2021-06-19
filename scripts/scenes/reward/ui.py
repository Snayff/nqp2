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

    def update(self):
        units = self.game.memory.player_troupe.units

        self.handle_directional_input_for_selection()

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            if self.selected_reward and self.game.reward.reward_type == RewardType.UNIT:
                if isinstance(self.selected_reward, Unit):
                    self.game.reward.choose_troupe_reward(self.selected_reward)
                    self.game.training.upgrade_unit(self.selected_reward.id)
                else:
                    logging.warning(f"Chose {self.selected_reward} as a unit reward. As it isnt a unit something has "
                                    f"seriously gone wrong! No reward added")

        # exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.TROUPE)

        # manage looping
        self.handle_selected_index_looping(len(units))

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

    def _render_unit_rewards(self, surface: pygame.surface):

        reward_units = list(self.game.reward.troupe_rewards.units.values())
        default_font = self.default_font
        disabled_font = self.disabled_font
        warning_font = self.warning_font
        stats = ["health", "defence", "attack", "range", "attack_speed", "move_speed", "ammo", "count"]

        # positions
        start_x = 20
        start_y = 60
        gap = 10
        font_height = 12
        window_width = self.game.window.width
        col_width = int((window_width - (start_x * 2)) / len(stats))

        # draw headers
        col_count = 0
        for stat in stats:
            col_x = start_x + (col_width * col_count)
            default_font.render(stat, surface, (col_x, start_y))

            col_count += 1

        # draw unit info
        row_count = 0
        for unit in reward_units:
            active_font = default_font

            option_y = start_y + ((font_height + gap) * (row_count + 1))  # + 1 due to headers

            # draw stats
            col_count = 0
            for stat in stats:
                col_x = start_x + (col_width * col_count)

                # draw type or state value
                if col_count == 0:
                    text = unit.type
                else:
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

            # show gold
            self.draw_gold(surface)
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, PostCombatState, RewardType, SceneType
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Optional

    from scripts.core.game import Game

__all__ = ["PostCombatUI"]


################ TO DO LIST ##################


class PostCombatUI(UI):
    """
    Represent the UI of the RewardScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_reward: Optional[Unit] = None

        self.set_instruction_text("Choose your rewards.")

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.game.post_combat.state == PostCombatState.VICTORY:
            self.handle_victory_input()
        elif self.game.post_combat.state == PostCombatState.DEFEAT:
            self.handle_defeat_input()

    def render(self, surface: pygame.surface):
        if self.game.post_combat.state == PostCombatState.VICTORY:

            reward_type = self.game.post_combat.reward_type
            if reward_type == RewardType.UNIT:
                pass
                # self._render_unit_rewards(surface)

            elif reward_type == RewardType.ACTION:
                pass

            elif reward_type == RewardType.UPGRADE:
                pass

            else:
                # reward_type == RewardType.RESOURCE
                pass

            # show core info
            self.draw_instruction(surface)

        elif self.game.post_combat.state == PostCombatState.DEFEAT:
            self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        if self.game.post_combat.state == PostCombatState.VICTORY:
            self._rebuild_victory_ui()
        elif self.game.post_combat.state == PostCombatState.DEFEAT:
            self._rebuild_defeat_ui()

        self.rebuild_resource_elements()

    def _rebuild_victory_ui(self):
        default_font = self.default_font
        positive_font = self.positive_font

        start_x = 20
        start_y = 40
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        font_height = default_font.height
        window_width = self.game.window.width
        window_height = self.game.window.height

        # draw header
        header_text = "Victory"
        current_x = window_width // 2 - (default_font.width(header_text))
        current_y = start_y
        frame = Frame(
            (current_x, current_y),
            text_and_font=(header_text, positive_font),
            is_selectable=False,
        )
        self.elements["header"] = frame

        # draw gold reward
        current_y += 50
        gold_icon = self.game.assets.get_image("stats", "gold", icon_size)
        gold_reward = self.game.post_combat.gold_reward
        frame = Frame(
            (current_x, current_y),
            image=gold_icon,
            text_and_font=(str(gold_reward), default_font),
            is_selectable=False,
        )
        self.elements["gold_reward"] = frame

        # draw exit button
        self.add_exit_button()

    def _rebuild_defeat_ui(self):
        default_font = self.default_font
        negative_font = self.warning_font

        start_x = 20
        start_y = 40
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        font_height = default_font.height
        window_width = self.game.window.width
        window_height = self.game.window.height

        self.set_instruction_text("Return to the main menu")

        # draw header
        header_text = "Defeat"
        current_x = window_width // 2 - (default_font.width(header_text))
        current_y = start_y
        frame = Frame(
            (current_x, current_y),
            text_and_font=(header_text, negative_font),
            is_selectable=False,
        )
        self.elements["header"] = frame

        # draw exit button
        self.add_exit_button()

    def _render_unit_rewards(self, surface: pygame.surface):
        pass
        # # FIXME - this no longer works
        # reward_units = list(self.game.reward.troupe_rewards.units.values())
        # default_font = self.default_font
        # disabled_font = self.disabled_font
        # warning_font = self.warning_font
        # positive_font = self.positive_font
        # stats = ["type", "health", "defence", "attack", "range", "attack_speed", "move_speed", "projectiles", "count"]
        #
        # # positions
        # start_x = 20
        # start_y = 40
        # font_height = 12
        # window_width = self.game.window.width
        # window_height = self.game.window.height
        # col_width = int((window_width - (start_x * 2)) / len(stats))
        #
        # # victory message
        # positive_font.render("Victory!", surface, (start_x, start_y))
        #
        # # gold reward
        # current_y = start_y + (font_height * 2)
        # gold_reward = self.game.reward.gold_reward
        # default_font.render(f"{gold_reward} gold scavenged from the dead.", surface, (start_x, current_y))
        #
        # # instruction
        # current_y = window_height // 2
        # warning_font.render(f"Choose one of the following rewards.", surface, (start_x, current_y))
        #
        # # draw headers
        # current_y = current_y + (font_height * 2)
        # col_count = 0
        # for stat in stats:
        #     col_x = start_x + (col_width * col_count)
        #     default_font.render(stat, surface, (col_x, current_y))
        #
        #     col_count += 1
        #
        # # draw unit info
        # row_count = 0
        # for unit in reward_units:
        #     active_font = default_font
        #
        #     option_y = current_y + ((font_height + GAP_SIZE) * (row_count + 1))  # + 1 due to headers
        #
        #     # draw stats
        #     col_count = 0
        #     for stat in stats:
        #         col_x = start_x + (col_width * col_count)
        #
        #         text = str(getattr(unit, stat))
        #         active_font.render(text, surface, (col_x, option_y))
        #
        #         col_count += 1
        #
        #     # draw selector
        #     if row_count == self.selected_row:
        #         # note the selected unit
        #         self.selected_reward = unit
        #
        #         pygame.draw.line(
        #             surface,
        #             (255, 255, 255),
        #             (start_x, option_y + font_height),
        #             (start_x + active_font.width(unit.type), option_y + font_height),
        #         )
        #
        #     row_count += 1

    def handle_victory_input(self):
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # there's only 1 thing to select so we know it is the exit button
            self.game.change_scene(SceneType.OVERWORLD)

    def handle_defeat_input(self):
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # there's only 1 thing to select so we know it is the exit button
            self.game.run_setup.reset()
            self.game.change_scene(SceneType.MAIN_MENU)

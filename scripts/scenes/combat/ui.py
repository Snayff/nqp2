from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import CombatState, SceneType
from scripts.core.utility import offset
from scripts.ui_elements.tooltip import Tooltip

if TYPE_CHECKING:
    from scripts.core.game import Game
    from scripts.scenes.combat.scene import CombatScene

__all__ = ["CombatUI"]


class CombatUI(UI):
    def __init__(self, game: Game, parent_scene: CombatScene):
        super().__init__(game, True)
        self.parent_scene: CombatScene = parent_scene

        # position relative to terrain
        self.place_target = [
            self.game.window.base_resolution[0] // 8,
            self.game.window.base_resolution[1] // 2,
        ]
        self.selected_col = 0
        self.button_scroll = 0
        self.shown_buttons = 4

    def update(self, delta_time: float):
        super().update(delta_time)

        # don't move camera until all units are placed (also skip if the ending animation is playing)
        if (self.game.combat.general_state == "actions") and (self.game.combat.combat_ending_timer == -1):
            target_pos = self.game.combat.get_team_center("player")
            if not target_pos:
                target_pos = [0, 0]
            else:
                target_pos[0] -= self.game.window.base_resolution[0] // 2
                target_pos[1] -= self.game.window.base_resolution[1] // 2

            self.game.combat.camera.pos[0] += (
                (target_pos[0] - self.game.combat.camera.pos[0]) / 10 * (self.game.window.delta_time * 60)
            )
            self.game.combat.camera.pos[1] += (
                (target_pos[1] - self.game.combat.camera.pos[1]) / 10 * (self.game.window.delta_time * 60)
            )

        # scroll buttons to fit current col
        if self.selected_col >= self.button_scroll + self.shown_buttons:
            self.button_scroll = self.selected_col - self.shown_buttons + 1
        if self.selected_col < self.button_scroll:
            self.button_scroll = self.selected_col

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        if self.game.combat.state in [CombatState.UNIT_CHOOSE_CARD, CombatState.ACTION_CHOOSE_CARD]:

            if self.game.input.states["left"]:
                self.game.input.states["left"] = False

                self.selected_col -= 1
                if self.selected_col < 0:
                    self.selected_col = self.button_count - 1

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False

                self.selected_col += 1
                if self.selected_col > self.button_count - 1:
                    self.selected_col = 0

            if self.game.input.states["select"]:

                # transition to appropriate mode
                if self.game.combat.state == CombatState.UNIT_CHOOSE_CARD:
                    # can only use a card if there are cards in your hand and point limit not hit
                    if self.game.combat.units_are_available[self.selected_col]:
                        unit = self.game.memory.player_troupe._units[
                            self.game.combat.placeable_units[self.selected_col]
                        ]
                        leadership = self.game.memory.leadership
                        leadership_remaining = leadership - self.game.combat.leadership_points_spent
                        if self.button_count and leadership_remaining >= unit.tier:
                            self.game.combat.state = CombatState.UNIT_SELECT_TARGET
                else:
                    if not self.game.combat.skill_cooldowns[self.selected_col]:
                        # determine action target mode
                        target_type = action = self.game.combat.actions[
                            self.game.memory.player_actions[self.selected_col]
                        ](self.game).target_type
                        if target_type == "free":
                            self.game.combat.state = CombatState.ACTION_SELECT_TARGET_FREE

            if self.game.input.states["cancel"]:
                if self.game.combat.state == CombatState.UNIT_CHOOSE_CARD:
                    pass

                self.game.combat.state = CombatState.WATCH

        elif self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
            directions = {
                "right": (1, 0),
                "left": (-1, 0),
                "up": (0, -1),
                "down": (0, 1),
            }

            move_amount = [0, 0]

            # add up direction movement
            for direction in directions:
                if self.game.input.states["hold_" + direction]:
                    offset(move_amount, directions[direction], self.game.window.delta_time * 175)

            self.place_target = offset(self.place_target, move_amount)

            # constrain placements for units
            if self.game.combat.general_state == "units":
                self.place_target[0] = min(self.game.window.base_resolution[0] // 4, max(0, self.place_target[0]))
                self.place_target[1] = min(self.game.window.base_resolution[1], max(0, self.place_target[1]))

            if self.game.input.states["select"]:
                # hand will contain the hand for whichever deck is in use
                if self.game.combat.state == CombatState.UNIT_SELECT_TARGET:
                    unit = self.game.memory.player_troupe._units[self.game.combat.placeable_units[self.selected_col]]
                    self.game.combat.units_are_available[self.selected_col] = False
                    unit.pos = self.place_target.copy()
                    self.game.combat.leadership_points_spent += unit.tier
                    self.game.combat.units.add_unit_to_combat(unit)

                    logging.debug(f"Placed {unit.type}({unit.id}) at {unit.pos}.")
                else:
                    action = self.game.combat.actions[self.game.memory.player_actions[self.selected_col]](self.game)
                    self.game.combat.skill_cooldowns[self.selected_col] = self.game.data.skills[action.type]["cooldown"]
                    action.use(self.place_target.copy())

            if self.game.input.states["cancel"] or self.game.input.states["select"]:
                # transition to appropriate state
                if self.game.combat.state == CombatState.UNIT_SELECT_TARGET:
                    self.game.combat.state = CombatState.UNIT_CHOOSE_CARD
                else:
                    self.game.combat.state = CombatState.ACTION_CHOOSE_CARD

        elif self.game.combat.state == CombatState.WATCH:
            if self.game.input.states["cancel"]:
                self.game.combat.state = CombatState.ACTION_CHOOSE_CARD
                self.game.combat.start_action_phase()

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

    @property
    def button_count(self):
        if self.game.combat.general_state == "units":
            return len(self.game.combat.placeable_units)
        elif self.game.combat.general_state == "actions":
            return len(self.game.memory.player_actions)

    def render_buttons(self, surface: pygame.Surface):
        background_surf = pygame.transform.scale(self.game.assets.ui["rounded_box"].copy(), (40, 40))
        background_surf.set_alpha(180)
        selected_surf = pygame.transform.scale(self.game.assets.ui["rounded_box_outline"], (40, 40))
        red_selected_surf = pygame.transform.scale(self.game.assets.ui["rounded_box_outline_red"], (40, 40))
        margin = 4

        if self.game.combat.general_state == "units":
            id_list = self.game.combat.placeable_units
        elif self.game.combat.general_state == "actions":
            id_list = self.game.memory.player_actions
        else:
            return None

        for i, obj_id in enumerate(id_list):
            if self.button_scroll <= i < self.button_scroll + self.shown_buttons:
                x = i - self.button_scroll
                button_pos = (
                    margin + x * (background_surf.get_width() + margin),
                    surface.get_height() - margin - background_surf.get_height(),
                )
                can_use = True

                if self.game.combat.general_state == "units":
                    obj_img = pygame.transform.scale(
                        self.game.assets.unit_animations[self.game.memory.player_troupe._units[obj_id].type]["icon"][
                            0
                        ].copy(),
                        (32, 32),
                    )
                    if not self.game.combat.units_are_available[i]:
                        obj_img.set_alpha(100)
                        can_use = False
                elif self.game.combat.general_state == "actions":
                    obj_img = pygame.transform.scale(self.game.assets.actions[obj_id].copy(), (32, 32))
                    if self.game.combat.skill_cooldowns[i]:
                        obj_img.set_alpha(100)
                        can_use = False

                surface.blit(background_surf, button_pos)
                surface.blit(obj_img, (button_pos[0] + 4, button_pos[1] + 4))

                # cooldown overlay
                if (not can_use) and (self.game.combat.general_state == "actions"):
                    cooldown_img = background_surf.copy()
                    cooldown_img.set_alpha(200)
                    cooldown = (
                        self.game.combat.skill_cooldowns[i]
                        / self.game.data.skills[self.game.memory.player_actions[i]]["cooldown"]
                    )
                    cooldown_offset = int(cooldown_img.get_height() * cooldown)
                    cooldown_img = cooldown_img.subsurface(
                        pygame.Rect(
                            0, cooldown_img.get_height() - cooldown_offset, cooldown_img.get_width(), cooldown_offset
                        )
                    )
                    surface.blit(
                        cooldown_img, (button_pos[0], button_pos[1] + background_surf.get_height() - cooldown_offset)
                    )

                if self.game.combat.state != CombatState.WATCH:
                    if i == self.selected_col:
                        if can_use:
                            surface.blit(selected_surf, button_pos)
                        else:
                            surface.blit(red_selected_surf, button_pos)

    def render(self, surface: pygame.Surface):
        if self.game.combat.general_state == "units":
            # render friendly/enemy spawn areas
            friendly_surf = pygame.Surface((int(surface.get_width() * 0.25), surface.get_height()))
            enemy_surf = friendly_surf.copy()
            friendly_surf.fill((50, 250, 150))
            enemy_surf.fill((250, 150, 50))
            friendly_surf.set_alpha(90)
            enemy_surf.set_alpha(90)
            surface.blit(friendly_surf, (0, 0))
            surface.blit(enemy_surf, (surface.get_width() - enemy_surf.get_width(), 0))

        self.draw_instruction(surface)
        self.draw_elements(surface)

        # draw selector
        if self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
            placement_img = None
            if self.game.combat.state == CombatState.UNIT_SELECT_TARGET:
                obj_id = self.game.combat.placeable_units[self.selected_col]
                placement_img = self.game.assets.unit_animations[self.game.memory.player_troupe._units[obj_id].type][
                    "idle"
                ][0]
            if self.game.combat.state == CombatState.ACTION_SELECT_TARGET_FREE:
                # needs some assets to indicate placement of the action
                pass

            if placement_img:
                render_base = self.game.combat.camera.render_offset(self.place_target)
                surface.blit(
                    placement_img,
                    (render_base[0] - placement_img.get_width() // 2, render_base[1] - placement_img.get_height() // 2),
                )
            pygame.draw.circle(surface, (255, 255, 255), self.game.combat.camera.render_offset(self.place_target), 8, 1)

        self.render_buttons(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        # render status text
        status = "None"
        if self.game.combat.state in [CombatState.UNIT_SELECT_TARGET, CombatState.ACTION_SELECT_TARGET_FREE]:
            status = "select a target location"
        elif self.game.combat.state == CombatState.UNIT_CHOOSE_CARD:
            status = "select a unit or press X to end unit placement"
        elif self.game.combat.state == CombatState.ACTION_CHOOSE_CARD:
            status = "select an action or press X to watch"
        elif self.game.combat.state == CombatState.WATCH:
            status = "press X to use an action"
        self.set_instruction_text(status)

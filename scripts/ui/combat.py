from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.elements.unit import Unit
from scripts.misc.constants import CombatState
from scripts.misc.utility import offset


class CombatUI:
    def __init__(self, game):
        self.game = game

        self.selected_card = 0  # card index

        # position relative to terrain
        self.place_target = [0, 0]

    def update(self):
        cards = self.game.combat.hand.cards

        if self.game.combat.state == CombatState.CHOOSE_CARD:
            if self.game.input.states["left"]:
                self.game.input.states["left"] = False
                self.selected_card -= 1
                if self.selected_card < 0:
                    self.selected_card = len(cards) - 1

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False
                self.selected_card += 1
                if self.selected_card >= len(cards):
                    self.selected_card = 0

            if self.game.input.states["select"]:
                self.game.combat.state = CombatState.SELECT_TARGET
                self.place_target = [
                    self.game.combat.terrain.pixel_size[0] // 2,
                    self.game.combat.terrain.pixel_size[1] // 2,
                ]

        elif self.game.combat.state == CombatState.SELECT_TARGET:
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
                    offset(move_amount, directions[direction], self.game.window.dt * 75)

            self.place_target = offset(self.place_target, move_amount)

            if self.game.input.states["select"]:
                self.game.combat.units.add_unit(
                    Unit(self.game.combat.hand.cards[self.selected_card].type, self.place_target)
                )
                self.game.combat.hand.cards.pop(self.selected_card)
                self.game.combat.state = CombatState.WATCH

    def render(self, surface: pygame.Surface):
        cards = self.game.combat.hand.cards

        if self.game.combat.state == CombatState.SELECT_TARGET:
            pygame.draw.circle(surface, (255, 255, 255), self.game.combat.camera.render_offset(self.place_target), 8, 1)

        if self.game.combat.state != CombatState.WATCH:
            start_pos = self.game.window.display.get_width() // 2 - (len(cards) - 1) * 30

            for i, card in enumerate(cards):
                height_offset = 0
                if self.selected_card == i:
                    height_offset = -12

                elif self.game.combat.state == CombatState.SELECT_TARGET:
                    height_offset += 12

                card.render(surface, (start_pos + i * 60 - 25, 300 + height_offset))

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.scenes.combat.elements.unit import Unit
from scripts.core.constants import CombatState
from scripts.core.utility import offset

if TYPE_CHECKING:
    pass


class CombatUI(UI):
    def __init__(self, game):
        super().__init__(game)

        self.selected_card = 0  # card index

        # position relative to terrain
        self.place_target = [0, 0]

    def update(self):
        cards = self.game.combat.hand.cards

        if self.game.combat.state == CombatState.CHOOSE_CARD:
            if self.game.input.states["left"]:
                self.game.input.states["left"] = False
                self.selected_card -= 1

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False
                self.selected_card += 1

            if self.game.input.states["select"]:
                self.game.combat.state = CombatState.SELECT_TARGET
                self.place_target = [
                    self.game.combat.terrain.pixel_size[0] // 2,
                    self.game.combat.terrain.pixel_size[1] // 2,
                ]

            if self.game.input.states["cancel"]:
                self.game.combat.state = CombatState.WATCH

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
                    Unit(self.game, self.game.combat.hand.cards[self.selected_card].type, self.place_target)
                )
                self.game.combat.hand.cards.pop(self.selected_card)
                self.game.combat.state = CombatState.CHOOSE_CARD

            if self.game.input.states["cancel"]:
                self.game.combat.state = CombatState.CHOOSE_CARD

        # correct card selection index for looping
        if self.selected_card < 0:
            self.selected_card = len(cards) - 1
        if self.selected_card >= len(cards):
            self.selected_card = 0

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


## TO DO LIST ##
# TODO -  Win state/ lose state; when all of one side is dead.
# TODO - show bar that is all of remaining health for both sides as a % of total. So when player is winning the bar
#  will progress to one side and if the opposite then it will progress to the other.
# TODO - dev tool - instant win button
# TODO - dont start combat until all units placed / units up to limit placed
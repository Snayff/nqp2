from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel
from scripts.ui_elements.unit_stats_frame import UnitStatsFrame

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["InnUI"]

########### To Do List #############
# TODO - Add button for going back to  overworld


class InnUI(UI):
    """
    Represent the UI of the InnScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.set_instruction_text("Choose your newest recruits.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # generic input
        # directional input
        if self.game.input.states["right"]:
            self.game.input.states["right"] = False

            self.current_panel.select_next_element()

        if self.game.input.states["left"]:
            self.game.input.states["left"] = False

            self.current_panel.select_previous_element()

        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

        # panel specific input
        if self.current_panel == self.panels["buy"]:
            self.handle_buy_input()

        elif self.current_panel == self.panels["exit"]:
            self.handle_exit_input()

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_gold(surface)
        self.draw_charisma(surface)
        self.draw_leadership(surface)
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        units_for_sale = list(self.game.inn.sale_troupe.units.values())
        default_font = self.default_font
        warning_font = self.warning_font
        font_height = 12  # FIXME - get actual font height
        window_width = self.game.window.width
        window_height = self.game.window.height

        # positions
        start_x = 20
        start_y = 20

        # draw unit info
        current_x = start_x
        panel_list = []
        count = -1
        for unit in units_for_sale:
            count += 1
            print(f"UnitsForSale: {count}: {unit.type}")

            # check can purchase
            can_afford = unit.gold_cost <= self.game.memory.gold
            has_enough_charisma = self.game.memory.commander.charisma_remaining > 0
            if can_afford and has_enough_charisma:
                active_font = default_font
            else:
                active_font = warning_font

            # draw buy option
            current_y = start_y
            frame = Frame((current_x, current_y), text_and_font=("Buy", active_font), is_selectable=True)
            self.elements[f"{unit.type}"] = frame
            panel_list.append(frame)

            # draw unit
            current_y += 30
            frame = UnitStatsFrame(
                self.game,
                (current_x, current_y),
                unit,
            )
            self.elements[f"{unit.type}_stats"] = frame

            # increment pos
            current_x += 70

        # store panel info
        self.panels["buy"] = Panel(panel_list, True)
        self.current_panel = self.panels["buy"]
        self.current_panel.select_first_element()

        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (font_height + GAP_SIZE)
        frame = Frame((current_x, current_y), text_and_font=(confirm_text, default_font), is_selectable=True)
        self.elements["exit"] = frame
        panel = Panel([frame], True)
        self.add_panel(panel, "exit")

    def handle_buy_input(self):
        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # get selected unit
            units = list(self.game.inn.sale_troupe.units.values())
            unit = units[self.current_panel.selected_index]

            # can we purchase
            can_afford = unit.gold_cost <= self.game.memory.gold
            has_enough_charisma = self.game.memory.commander.charisma_remaining > 0
            if can_afford and has_enough_charisma:
                self.game.inn.purchase_unit(unit)

                self.rebuild_ui()

                self.set_instruction_text(f"{unit.type} recruited!", True)

            else:
                # inform player of fail states
                if not can_afford:
                    self.set_instruction_text(f"You can't afford the {unit.type}.", True)
                else:
                    self.set_instruction_text(f"You don't have enough charisma to recruit them.", True)

        # exit
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # unselect current panel
            self.current_panel.unselect_all_elements()

            # change to exit panel
            self.current_panel = self.panels["exit"]
            self.current_panel.select_first_element()

    def handle_exit_input(self):
        # exit
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # return to overworld
            self.game.change_scene(SceneType.OVERWORLD)

        # return to selections
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # unselect current panel
            self.current_panel.unselect_all_elements()

            # change to buy panel
            self.current_panel = self.panels["buy"]
            self.current_panel.select_first_element()

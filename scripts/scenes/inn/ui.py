from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, SceneType
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel
from scripts.ui_elements.unit_stats_frame import UnitStatsFrame

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

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

        self.selected_unit: Optional[Unit] = None
        self.stat_frame: Optional[UnitStatsFrame] = None
        self.stat_frame_pos: Tuple[int, int] = (0, 0)

        self.set_instruction_text("Choose your newest recruits.")

    def update(self, delta_time: float):
        super().update(delta_time)

        # generic input
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
        self.draw_instruction(surface)

        # draw elements
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        scene = self.game.inn
        units_for_sale = list(scene.sale_troupe.units.values())
        default_font = self.default_font
        warning_font = self.warning_font
        disabled_font = self.disabled_font

        start_x = 20
        start_y = 40
        font_height = 12  # FIXME - get actual font height
        window_width = self.game.window.width
        window_height = self.game.window.height
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)

        # draw units
        current_x = start_x
        current_y = start_y
        panel_list = []
        for selection_counter, unit in enumerate(units_for_sale):
            # check if available
            if scene.units_available[unit.id]:
                text = f"{unit.type}"
                font = default_font
                is_selectable = True

                # check can afford
                can_afford = unit.gold_cost <= self.game.memory.gold
                has_enough_charisma = self.game.memory.commander.charisma_remaining > 0
                if can_afford and has_enough_charisma:
                    gold_font = default_font
                else:
                    gold_font = warning_font

                # draw gold cost
                gold_icon = self.game.assets.get_image("stats", "gold", icon_size)
                frame = Frame(
                    (current_x, current_y),
                    image=gold_icon,
                    text_and_font=(str(unit.gold_cost), gold_font),
                    is_selectable=False,
                )
                self.elements["cost" + str(selection_counter)] = frame

            else:
                text = f"Recruited"
                font = disabled_font
                is_selectable = False

            # draw unit icon and details
            unit_x = current_x + 50
            stat_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
            frame = Frame(
                (unit_x, current_y),
                image=stat_icon,
                text_and_font=(text, font),
                is_selectable=is_selectable,
            )
            # capture frame
            self.elements[f"{unit.id}_{selection_counter}"] = frame
            panel_list.append(frame)

            # highlight selected unit
            if self.selected_unit is None:
                self.selected_unit = unit
            if unit.type == self.selected_unit:
                frame.is_selected = True

            # increment
            current_y += icon_height + GAP_SIZE

        # add units to a panel
        self.panels["buy"] = Panel(panel_list, True)
        self.current_panel = self.panels["buy"]
        self.current_panel.select_first_element()

        # draw stat frame
        current_x += 150
        unit_stat_y = start_y + 20
        frame = UnitStatsFrame(self.game, (current_x, unit_stat_y), self.selected_unit)
        self.elements["stat_frame"] = frame

        # exit button
        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (font_height + GAP_SIZE)
        frame = Frame((current_x, current_y), text_and_font=(confirm_text, default_font), is_selectable=True)
        self.elements["exit"] = frame
        panel = Panel([frame], True)
        self.add_panel(panel, "exit")

        self.rebuild_resource_elements()

    def refresh_info(self):
        elements = self.elements

        if self.selected_unit is not None:
            elements["stat_frame"].set_unit(self.selected_unit)

    def handle_buy_input(self):
        if self.game.input.states["down"]:
            self.game.input.states["down"] = False

            self.current_panel.select_next_element()
            self.selected_unit = list(self.game.inn.sale_troupe.units.values())[self.current_panel.selected_index]
            self.refresh_info()  # for stat panel

        if self.game.input.states["up"]:
            self.game.input.states["up"] = False

            self.current_panel.select_previous_element()
            self.selected_unit = list(self.game.inn.sale_troupe.units.values())[self.current_panel.selected_index]
            self.refresh_info()  # for stat panel

        # select option and trigger result
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # get selected unit
            units = list(self.game.inn.sale_troupe.units.values())
            unit = units[self.current_panel.selected_index]

            # is available
            if self.game.inn.units_available[unit.id]:

                # can we purchase
                can_afford = unit.gold_cost <= self.game.memory.gold
                has_enough_charisma = self.game.memory.commander.charisma_remaining > 0
                if can_afford and has_enough_charisma:
                    self.game.inn.purchase_unit(unit)

                    self.rebuild_ui()

                    self.set_instruction_text(f"{unit.id} recruited!", True)

                    # check if anything left available
                    if True in self.game.inn.units_available.values():
                        self.set_instruction_text("Choose an upgrade to buy.")
                    else:
                        self.set_instruction_text("All sold out. Time to move on.")

                        # unselect current panel
                        self.current_panel.unselect_all_elements()

                        # change to exit panel
                        self.current_panel = self.panels["exit"]
                        self.current_panel.select_first_element()

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

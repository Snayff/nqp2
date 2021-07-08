from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE, SceneType, TrainingState
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.unit_stats_frame import UnitStatsFrame

if TYPE_CHECKING:
    from typing import List, Tuple, Dict
    from scripts.core.game import Game

__all__ = ["TrainingUI"]


class TrainingUI(UI):
    """
    Represent the UI of the TrainingScene.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_unit: Optional[Unit] = None
        self.selected_upgrade: Optional[Dict] = None
        self.stat_frame: Optional[UnitStatsFrame] = None
        self.stat_frame_pos: Tuple[int, int] = (0, 0)
        self.column_descriptors: Dict = {}  # col description: col number

        self.set_instruction_text("Choose who to upgrade.")

        self.rebuild_selection_array(3, 10)

    def update(self, delta_time: float):
        super().update(delta_time)

        # N.B. does not use default handle_directional_input_for_selection method
        self.handle_directional_input_for_selection()

        # handle selection based on selector position
        if self.selected_col == self.column_descriptors["upgrades"]:
            self.handle_select_upgrade_input()

        elif self.selected_col == self.column_descriptors["units"]:
            self.handle_choose_unit_input()

        elif self.selected_col == self.column_descriptors["exit"]:
            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                self.game.change_scene(SceneType.OVERWORLD)

        # view troupe, this is universally accessible
        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.surface):

        # TESTING
        self.set_instruction_text(f"Selected row: {self.selected_row}, Selected col: {self.selected_col}"
                                  f"; Max row: {self.max_rows}, Max col: {self.max_cols} ; "
                                  f"Last row: {self.last_row}, Last col: {self.last_col}")

        # show core info
        self.draw_gold(surface)
        self.draw_charisma(surface)
        self.draw_leadership(surface)
        self.draw_instruction(surface)

        # draw elements
        self.draw_element_array(surface)

    def rebuild_ui(self):
        default_font = self.default_font
        scene = self.game.training

        start_x = 20
        start_y = 20
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        font_height = 12  # FIXME - get actual font height
        window_width = self.game.window.width
        window_height = self.game.window.height

        # draw upgrades
        current_x = start_x
        current_y = start_y
        col_number = 0
        self.column_descriptors["upgrades"] = col_number
        for selection_counter, upgrade in enumerate(scene.upgrades_sold):
            # TODO - draw gold cost
            stat_icon = self.game.assets.get_image("stats", upgrade["stat"], icon_size)
            frame = Frame(
                (current_x, current_y),
                image=stat_icon,
                text_and_font=(f"{upgrade['stat']} +{upgrade['mod_amount']}", default_font),
                is_selectable=True
                )
            self.element_array[col_number][selection_counter] = frame

            # highlight selected upgrade
            if upgrade["type"] == self.selected_upgrade or self.selected_upgrade is None:
                frame.is_selected = True

            # increment
            current_y += icon_height + GAP_SIZE

        # draw unit selection
        if scene.state == TrainingState.CHOOSE_TARGET_UNIT:
            col_number += 1
            self.column_descriptors["units"] = col_number

            # draw list of units
            current_x = start_x + 100
            current_y = start_y + 20  # add an offset
            for selection_counter, unit in enumerate(self.game.memory.player_troupe.units.values()):
                unit_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
                self.element_array[col_number][selection_counter] = Frame(
                    (current_x, current_y),
                    image=unit_icon,
                    text_and_font=(f"{unit.type}", default_font),
                    is_selectable=True
                )

                # increment
                current_y += icon_height + GAP_SIZE

            # draw stat frame
            col_number += 1
            self.column_descriptors["stat_frame"] = col_number
            current_x += 100
            if self.selected_unit:
                frame = UnitStatsFrame(self.game, self.stat_frame_pos, (400, 400), self.selected_unit)
                self.stat_frame = frame


        col_number += 1
        self.column_descriptors["exit"] = col_number
        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (font_height + GAP_SIZE)
        self.element_array[2][0] = Frame(
            (current_x, current_y),
            text_and_font=(confirm_text, default_font)
        )

    def handle_select_upgrade_input(self):
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # select the upgrade
            self.selected_upgrade = self.game.training.upgrades_sold[self.selected_row]

            # move to selecting unit
            self.increment_selected_col()
            self.game.training.state = TrainingState.CHOOSE_TARGET_UNIT
            self.selected_row = 0

            self.rebuild_ui()

    def handle_choose_unit_input(self):
        # return to upgrade select
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # clear selected upgrade
            self.selected_upgrade = None

            # move to select upgrade
            self.decrement_selected_col()
            self.game.training.state = TrainingState.CHOOSE_UPGRADE

            self.rebuild_ui()

        # choose a unit
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # do we have info needed
            if self.selected_unit and self.selected_upgrade:
                assert isinstance(self.selected_upgrade, dict)

                # can we afford
                id_ = self.selected_unit.id
                upgrade = self.selected_upgrade
                upgrade_cost = self.game.training.calculate_upgrade_cost(upgrade["tier"])
                if upgrade_cost <= self.game.memory.gold:

                    # pay for the upgrade and execute it
                    self.game.memory.amend_gold(-upgrade_cost)  # remove gold cost
                    self.game.memory.player_troupe.upgrade_unit(id_, upgrade["type"])

                    # remove upgrade from choices and refresh UI
                    self.game.training.upgrades_sold.pop(self.selected_row)

                    # confirm to user
                    self.set_instruction_text(f"{self.selected_unit.type} upgraded with {upgrade['type']}.")

                    # reset values to choose another upgrade
                    self.selected_unit = None
                    self.selected_upgrade = None
                    self.decrement_selected_col()
                    self.game.training.state = TrainingState.CHOOSE_UPGRADE

                    self.rebuild_ui()


                else:
                    self.set_instruction_text(f"You can't afford the {upgrade['type']} upgrade.", True)


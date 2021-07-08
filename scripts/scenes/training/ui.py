from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, SceneType, TrainingState
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

        self.set_instruction_text("Choose who to upgrade.")

        self.rebuild_selection_array(3, 10)

    def update(self, delta_time: float):
        super().update(delta_time)

        self.handle_selector_index_looping()
        # N.B. does not use default handle_directional_input_for_selection method

        # handle selection based on selector position
        if self.selected_col == 0:
            self.handle_select_upgrade_input()

        elif self.selected_col == 1:
            self.handle_choose_unit_input()

        # view troupe, this is universally accessible
        if self.game.input.states["view_troupe"]:
            self.game.input.states["view_troupe"] = False
            self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.surface):

        # show core info
        self.draw_gold(surface)
        self.draw_charisma(surface)
        self.draw_leadership(surface)
        self.draw_instruction(surface)

        # draw info for selected unit
        self.stat_frame_pos = (200, 40)
        if self.stat_frame:
            self.stat_frame.render(surface)

        # draw selectables
        self.draw_element_array(surface)

    def rebuild_ui(self):
        scene = self.game.training
        start_x = 20
        start_y = 20
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        gap = 2
        font_height = 12  # FIXME - get actual font height
        window_width = self.game.window.width
        window_height = self.game.window.height

        # TESTING
        self.set_instruction_text(f"Selected row: {self.selected_row}, Selected col: {self.selected_col}"
                                  f"; Max row: {self.max_rows}, Max col: {self.max_cols} ; "
                                  f"Last row: {self.last_row}, Last col: {self.last_col}")

        # draw upgrades
        current_x = start_x
        current_y = start_y
        for selection_counter, upgrade in enumerate(scene.upgrades_sold):
            # TODO - draw gold cost
            stat_icon = self.game.assets.get_image("stats", upgrade["stat"], icon_size)
            self.element_array[0][selection_counter] = Frame(self.game,
                                                             (current_x, current_y),
                                                             (100, 100),
                                                             stat_icon,
                                                               f"{upgrade['stat']} +{upgrade['mod_amount']}"
                                                             )

            # increment
            current_y += icon_height + gap

        # draw unit selection
        if scene.state == TrainingState.CHOOSE_TARGET_UNIT:

            # draw list of units
            current_x = start_x + 100  # add an offset
            current_y = start_y + 20
            for selection_counter, unit in enumerate(self.game.memory.player_troupe.units.values()):
                unit_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
                self.element_array[1][selection_counter] = Frame(self.game,
                                                                 (current_x, current_y),
                                                                 (100, 100),
                                                                 unit_icon,
                                                                   f"{unit.type}"
                                                                 )

                # increment
                current_y += icon_height + gap

        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + gap)
        current_y = window_height - (font_height + gap)
        self.element_array[2][0] = Frame(self.game,
                                         (current_x, current_y),
                                         (font_height, confirm_width),
                                         text=confirm_text
                                         )

    def handle_select_upgrade_input(self):
        if self.game.input.states["select"]:
            self.game.input.states["select"] = False

            # if on leave then exit to overworld
            if self.selected_row == self.last_row:
                self.game.change_scene(SceneType.OVERWORLD)

            else:

                # select the upgrade
                self.selected_upgrade = self.game.training.upgrades_sold[self.selected_row]

                # move to selecting unit
                self.selected_col += 1
                self.game.training.state = TrainingState.CHOOSE_TARGET_UNIT
                self.selected_row = 0

                self.refresh_stat_frame()


        # changing selection up or down
        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_row -= 1

            self.handle_selector_index_looping()

        elif self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_row += 1

            self.handle_selector_index_looping()

    def handle_choose_unit_input(self):
        # return to upgrade select
        if self.game.input.states["cancel"]:
            self.game.input.states["cancel"] = False

            # clear selected upgrade
            self.selected_upgrade = None

            # move to select upgrade
            self.selected_col -= 1
            self.game.training.state = TrainingState.CHOOSE_UPGRADE

            self.refresh_stat_frame()

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
                    self.refresh_dimensions()

                    # confirm to user
                    self.set_instruction_text(f"{self.selected_unit.type} upgraded with {upgrade['type']}.")

                    # reset values to choose another upgrade
                    self.selected_unit = None
                    self.selected_upgrade = None
                    self.selected_col -= 1
                    self.game.training.state = TrainingState.CHOOSE_UPGRADE


                else:
                    self.set_instruction_text(f"You can't afford the {upgrade['type']} upgrade.", True)

        # changing selection up or down
        if self.game.input.states["up"]:
            self.game.input.states["up"] = False
            self.selected_row -= 1

            self.handle_selector_index_looping()

            self.selected_unit = list(self.game.memory.player_troupe.units.values())[self.selected_row]
            self.refresh_stat_frame()

        elif self.game.input.states["down"]:
            self.game.input.states["down"] = False
            self.selected_row += 1

            self.handle_selector_index_looping()

            self.selected_unit = list(self.game.memory.player_troupe.units.values())[self.selected_row]
            self.refresh_stat_frame()

    def refresh_stat_frame(self):
        """
        Refresh the unit stat frame to show the selected unit info or remove if no selected unit.
        """
        self.stat_frame = None

        if self.selected_unit:
            frame = UnitStatsFrame(self.game, self.stat_frame_pos, (400, 400), self.selected_unit)
            self.stat_frame = frame


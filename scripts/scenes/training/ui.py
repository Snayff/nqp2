from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, SceneType, TrainingState
from scripts.scenes.combat.elements.unit import Unit
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

        self.dimensions: Dict[int, int] = {}
        self.last_row = 0

        self.set_instruction_text("Choose who to upgrade.")

    def update(self, delta_time: float):
        super().update(delta_time)

        self.set_selection_dimensions(len(self.dimensions.keys()), self.dimensions[self.selected_row])
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
        default_font = self.default_font
        warning_font = self.warning_font
        positive_font = self.positive_font
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

        # draw upgrades
        current_x = start_x
        current_y = start_y
        amount_x = current_x + icon_width + gap
        selection_counter = 0
        for upgrade in scene.upgrades_sold:

            # draw stat icon
            stat_icon = self.game.assets.get_image("stats", upgrade["stat"], icon_size)
            surface.blit(stat_icon, (current_x, current_y))

            # draw amount, + half font height to vertical centre it
            default_font.render(str(f"{upgrade['stat']} +{upgrade['mod_amount']}"),
                                surface, (amount_x, current_y + (font_height // 2)))

            # draw selector if on current row
            if selection_counter == self.selected_row:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (current_x, current_y + icon_height),
                    (current_x + default_font.width(upgrade["type"]), current_y + icon_height),
                )

            # draw selector on upgrade is choosing a unit
            if self.selected_upgrade:
                if upgrade["type"] == self.selected_upgrade["type"] and self.selected_col == 1:
                    pygame.draw.line(
                        surface,
                        (255, 255, 255),
                        (current_x, current_y + icon_height),
                        (current_x + default_font.width(upgrade["type"]), current_y + icon_height),
                    )

            # increment
            current_y += icon_height + gap
            selection_counter += 1

        # draw unit selection
        if scene.state == TrainingState.CHOOSE_TARGET_UNIT:

            # draw list of units
            current_x = start_x + 100  # add an offset
            current_y = start_y + 20
            selection_counter = 0
            for unit in self.game.memory.player_troupe.units.values():

                # draw unit icon
                unit_icon = self.game.assets.unit_animations[unit.type]["icon"][0]
                surface.blit(unit_icon, (current_x, current_y))

                # draw unit type, + half font height to vertical centre it
                default_font.render(unit.type, surface, (current_x + icon_width + gap, current_y + (font_height // 2)))

                # draw selector
                if selection_counter == self.selected_row and self.selected_col == 2:
                    pygame.draw.line(
                        surface,
                        (255, 255, 255),
                        (current_x, current_y + icon_height),
                        (current_x + default_font.width(unit.type), current_y + icon_height),
                    )

                # increment
                current_y += icon_height + gap
                selection_counter += 1

            # draw info for selected unit
            self.stat_frame_pos = (current_x + 100, start_y)
            if self.stat_frame:
                self.stat_frame.render(surface)

        # draw exit button
        confirm_text = "leave"
        confirm_width = default_font.width(confirm_text)
        current_x = window_width - (confirm_width + gap)
        current_y = window_height - (font_height + gap)
        default_font.render(confirm_text, surface, (current_x, current_y))

        # draw confirm selector
        print(f"Selected: {self.selected_row}, Last: {self.last_row}")
        if self.selected_row == self.last_row:
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (current_x, current_y + font_height),
                (current_x + confirm_width, current_y + font_height),
            )

        # show core info
        self.draw_gold(surface)
        self.draw_charisma(surface)
        self.draw_leadership(surface)
        self.draw_instruction(surface)

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

            elif self.game.input.states["down"]:
                self.game.input.states["down"] = False
                self.selected_row += 1

                self.handle_selector_index_looping()

                self.selected_unit = list(self.game.memory.player_troupe.units.values())[self.selected_row]

    def refresh_dimensions(self):
        self.dimensions = {}

        # add a row for each upgrade
        upgrades = self.game.training.upgrades_sold
        count = 0
        for count in range(len(upgrades)):
            self.dimensions[count] = 2  # set to 2 cols

        # add an extra row for the confirm button
        self.dimensions[count + 1] = 1  # set to 1 col


    def refresh_stat_frame(self):
        """
        Refresh the unit stat frame to show the selected unit info or remove if no selected unit.
        """
        self.stat_frame = None

        if self.selected_unit:
            frame = UnitStatsFrame(self.game, self.stat_frame_pos, self.selected_unit)
            self.stat_frame = frame


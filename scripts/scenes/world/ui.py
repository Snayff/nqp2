from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core import utility
from scripts.core.base_classes.ui import UI
from scripts.core.constants import ChooseRoomState, DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE, SceneType, TrainingState, \
    WorldState
from scripts.scene_elements.unit import Unit
from scripts.scene_elements.world.view import WorldView
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import List, Optional

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene


__all__ = ["WorldUI"]


class WorldUI(UI):
    """
    Receive and handle player input, passing off to the controller as required.
    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        super().__init__(game, False)
        self._parent_scene = parent_scene
        self._worldview = WorldView(game, parent_scene.model)

        self.grid: Optional[UnitGrid] = None

    def draw(self, surface: pygame.Surface):
        state = self._parent_scene.model.state

        self._worldview.draw(surface)

        # TODO: create and move to mouse tool system
        if state == WorldState.CHOOSE_NEXT_ROOM:
            if self.grid:
                self.grid.draw(surface)

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def update(self, delta_time: float):
        self._worldview.update(delta_time)

        state = self._parent_scene.model.state

        if state == WorldState.CHOOSE_NEXT_ROOM:
            self._update_idle(delta_time)
        elif state == WorldState.VICTORY:
            self._update_victory(delta_time)
        elif state == WorldState.TRAINING:
            self._update_training(delta_time)

    def _update_idle(self, delta_time: float):
        # need to call here as otherwise units dont align to grid
        # TODO - remove the need to call after init
        if self.grid is None:
            self.grid = UnitGrid(self._game)
            self.grid.move_units_to_grid()

    def _update_victory(self, delta_time: float):
        self._parent_scene.combat.victory_duration += delta_time
        if self._parent_scene.combat.victory_duration >= 3:
            self.rebuild_ui()

    def _update_training(self, delta_time: float):
        pass

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        state = self._parent_scene.model.state

        if state == WorldState.CHOOSE_NEXT_ROOM:
            self._process_choose_next_room_input()
        elif state == WorldState.DEFEAT:
            self._process_defeat_input()
        elif state == WorldState.TRAINING:
            self._process_training_input()

        if self.grid:
            self.grid.process_input()

    def _process_defeat_input(self):
        if self._game.input.states["select"]:
            self._game.memory.reset()
            self._game.change_scene(SceneType.MAIN_MENU)

    def _process_training_input(self):
        controller = self._parent_scene.training
        local_state = controller.state
        is_ui_dirty = False

        if local_state == TrainingState.IDLE:
            # toggle select upgrade or view units
            if self._game.input.states["shift"]:
                controller.state = TrainingState.CHOOSE_UPGRADE
                is_ui_dirty = True

        if local_state == TrainingState.CHOOSE_UPGRADE:
            # frame selection
            if self._game.input.states["up"]:
                self._current_panel.select_previous_element()
                is_ui_dirty = True
            if self._game.input.states["down"]:
                self._current_panel.select_next_element()
                is_ui_dirty = True

            # select upgrade
            if self._game.input.states["select"]:
                controller.state = TrainingState.CHOOSE_TARGET_UNIT
                controller.current_grid_index = 0
                is_ui_dirty = True

            # cancel
            if self._game.input.states["cancel"]:
                controller.state = TrainingState.IDLE
                is_ui_dirty = True

        if local_state == TrainingState.CHOOSE_TARGET_UNIT:
            # cancel
            if self._game.input.states["cancel"]:
                controller.state = TrainingState.CHOOSE_UPGRADE
                self.grid.units[controller.current_grid_index].is_selected = False
                is_ui_dirty = True

            # unit selection
            # TODO - update to allow moving around the grid rather than jumping indices
            current_index = controller.current_grid_index
            new_index = current_index
            if self._game.input.states["up"]:
                self.grid.units[current_index].is_selected = False
                new_index = utility.next_number_in_loop(current_index, len(self.grid.units))
            elif self._game.input.states["down"]:
                self.grid.units[current_index].is_selected = False
                new_index = utility.previous_number_in_loop(current_index, len(self.grid.units))

            controller.current_grid_index = new_index
            self.grid.units[new_index].is_selected = True

            # apply upgrade
            if self._game.input.states["select"]:
                controller.upgrade_unit(self.grid.units[current_index])

                # confirm
                self.set_instruction_text("Unit upgraded.", True)

                # revert to previous state
                self.grid.units[current_index].is_selected = False
                controller.state = TrainingState.CHOOSE_UPGRADE

                is_ui_dirty = True

        if is_ui_dirty:
            self.rebuild_ui()

    def _process_choose_next_room_input(self):
        controller = self._parent_scene.choose_room
        local_state = controller.state
        is_ui_dirty = False

        if local_state == ChooseRoomState.IDLE:
            # move to select room
            if self._game.input.states["shift"]:
                controller.state = ChooseRoomState.CHOOSE_ROOM
                is_ui_dirty = True

        if local_state == ChooseRoomState.CHOOSE_ROOM:
            # frame selection
            if self._game.input.states["up"]:
                self._current_panel.select_previous_element()
                is_ui_dirty = True
            if self._game.input.states["down"]:
                self._current_panel.select_next_element()
                is_ui_dirty = True

            # select upgrade
            if self._game.input.states["select"]:
                controller.begin_move_to_new_room()
                is_ui_dirty = True

            # cancel
            if self._game.input.states["cancel"]:
                controller.state = ChooseRoomState.IDLE
                is_ui_dirty = True

        if is_ui_dirty:
            self.rebuild_ui()

    def rebuild_ui(self):
        super().rebuild_ui()

        state = self._parent_scene.model.state

        if state == WorldState.CHOOSE_NEXT_ROOM:
            self._rebuild_choose_next_room_ui()
        elif state == WorldState.DEFEAT:
            self._rebuild_defeat_ui()
        elif state == WorldState.VICTORY:
            self._rebuild_victory_ui()
        elif state == WorldState.TRAINING:
            self._rebuild_training_ui()


    def _rebuild_choose_next_room_ui(self):
        create_font = self._game.visuals.create_font
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x, start_y = self._game.window.centre
        controller = self._parent_scene.choose_room
        model = self._parent_scene.model

        # draw room choices
        current_x = start_x
        current_y = start_y
        panel_list = []
        for i, room_and_if_hidden in enumerate(controller.choices):
            room_type, is_hidden = room_and_if_hidden

            # get icon
            if is_hidden:
                icon = self._game.visuals.get_image("unknown_room", icon_size)
                text = "Unknown"
            else:
                icon = self._game.visuals.get_image(room_type, icon_size)
                text = room_type
            frame = Frame(
                (current_x, current_y),
                new_image=icon,
                font=create_font(FontType.DEFAULT, text),
                is_selectable=True,
            )

            # register elements
            self._elements[room_type] = frame
            panel_list.append(frame)

        # build panel
        panel = Panel(panel_list)
        self.add_panel(panel, "room_choices")

        # handle instructions and selectability for different states
        if controller.state == ChooseRoomState.CHOOSE_ROOM:
            panel.set_selectable(True)
            self.set_instruction_text("Press X to cancel.")

            # ensure an room is selected
            if controller.selected_room is None:
                controller.selected_room = controller.choices[0][0]

            # highlight selected room
            highlighted_frame = self._elements[controller.selected_room]
            highlighted_frame.is_selected = True

        elif controller.state == ChooseRoomState.IDLE:
            panel.set_selectable(False)
            self.set_instruction_text("Press shift to select a room.")

    def _rebuild_training_ui(self):
        create_font = self._game.visuals.create_font
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x, start_y = self._game.window.centre
        controller = self._parent_scene.training
        model = self._parent_scene.model

        # draw upgrades
        current_x = start_x
        current_y = start_y
        panel_list = []
        for i, upgrade in enumerate(controller.upgrades_available):
            # check if available
            if upgrade is not None:
                text = f"{upgrade['stat']} +{upgrade['mod_amount']}"
                font_type = FontType.DEFAULT
                is_selectable = True

                # check can afford
                upgrade_cost = controller.calculate_upgrade_cost(upgrade["tier"])
                can_afford = model.gold > upgrade_cost
                if can_afford:
                    gold_font_type = FontType.DEFAULT
                else:
                    gold_font_type = FontType.NEGATIVE

                # draw gold cost
                gold_icon = self._game.visuals.get_image("gold", icon_size)
                frame = Frame(
                    (current_x, current_y),
                    new_image=gold_icon,
                    font=create_font(gold_font_type, str(upgrade_cost)),
                    is_selectable=False,
                )
                self._elements["cost" + str(i)] = frame

            else:
                text = f"Sold out"
                font_type = FontType.DISABLED
                is_selectable = False

            # draw upgrade icon and details
            upgrade_x = current_x + 50
            upgrade_icon = self._game.visuals.get_image(upgrade["type"], icon_size)
            frame = Frame(
                (upgrade_x, current_y),
                new_image=upgrade_icon,
                font=create_font(font_type, text),
                is_selectable=is_selectable,
            )
            # capture frame
            self._elements[upgrade["type"]] = frame
            panel_list.append(frame)

            # increment
            current_y += icon_height + GAP_SIZE

        panel = Panel(panel_list, True)
        self.add_panel(panel, "upgrades")

        # handle instructions and selectability for different states
        if controller.state == TrainingState.CHOOSE_UPGRADE:
            panel.set_selectable(True)
            self.set_instruction_text("Press X to cancel.")

            # ensure an upgrade is selected
            if controller.selected_upgrade is None:
                controller.selected_upgrade = controller.upgrades_available[0].copy()

            # highlight selected upgrade
            highlighted_frame = self._elements[controller.selected_upgrade["type"]]
            highlighted_frame.is_selected = True

            # show info pane
            info_x = highlighted_frame.x + highlighted_frame.width + 20
            font_type = FontType.DEFAULT
            upgrade = controller.selected_upgrade

            frame = Frame((info_x, highlighted_frame.y), font=create_font(font_type, upgrade["desc"]))
            self._elements["info_pane"] = frame

        elif controller.state == TrainingState.IDLE:
            panel.set_selectable(False)
            self.set_instruction_text("Press shift to select upgrades.")

        elif controller.state == TrainingState.CHOOSE_TARGET_UNIT:
            panel.set_selectable(False)
            self.set_instruction_text("Press enter to apply the upgrade or X to cancel.")

    def _rebuild_defeat_ui(self):
        create_font = self._game.visuals.create_font
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x, start_y = self._game.window.centre

        # draw upgrades
        current_x = start_x
        current_y = start_y
        defeat_icon = self._game.visuals.get_image("arrow_button", icon_size)
        frame = Frame(
            (current_x, current_y),
            new_image=defeat_icon,
            font=create_font(FontType.NEGATIVE, "Defeated"),
            is_selectable=False,
        )
        self._elements["defeat_notification"] = frame

        current_y += 100

        frame = Frame(
            (current_x, current_y),
            new_image=defeat_icon,
            font=create_font(FontType.DEFAULT, "Press Enter to return to the main menu."),
            is_selectable=False,
        )
        self._elements["defeat_instruction"] = frame

    def _rebuild_victory_ui(self):
        create_font = self._game.visuals.create_font
        start_x, start_y = self._game.window.centre

        # draw upgrades
        current_x = start_x
        current_y = start_y

        frame = Frame(
            (current_x, current_y),
            font=create_font(FontType.POSITIVE, "Victory"),
            is_selectable=False,
        )
        self._elements["victory_notification"] = frame


class GridCell:
    """
    A representation of the smallest discrete space in a Grid.
    """

    def __init__(self, rect: pygame.Rect, unit: Unit = None):
        self.rect = rect
        self.unit = unit


class UnitGrid:
    """
    An organised layout of rows and columns for Unit placement.
    """

    def __init__(self, game: Game):
        self.cell_size: int = 32  # Size of each cell
        self.cells_x_size: int = 3
        self.cells_y_size: int = 6  # Number of vertical and horizontal cells
        self.units: List[Unit] = game.world.model.get_all_units()  # Troupe units for placement
        self._game = game
        # TODO:
        #  - get the grid to move with the camera
        #  - support gamepad
        #  - show units moving on screen instead of setting their positions
        #  - there's still a bug somewhere that keeps units from switching placement
        self.margin_x = 16 * 5
        self.margin_y = 16 * 6
        self.are_units_aligned_to_grid = False
        self.selected_cell = None
        self.hover_cell = None

        # Initializes grid cells
        self.cells = [
            GridCell(pygame.Rect((self.margin_x + x, self.margin_y + y, self.cell_size, self.cell_size)))
            for y in range(0, self.cells_y_size * self.cell_size, self.cell_size)
            for x in range(0, self.cells_x_size * self.cell_size, self.cell_size)
        ]

        line_colour = (0, 100, 0)
        line_colour_hover = (0, 140, 0)
        line_colour_selected = (0, 180, 0)

        selected_hover_border_width = 3

        cell_rect = pygame.Rect((0, 0, self.cell_size, self.cell_size))

        # Surface for cells that were not selected, under current mouse position or gamepad selection
        self.cell_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface, line_colour, cell_rect, 1, 1)

        # Surface for the cell that's under the current mouse position or gamepad selection, but not selected
        self.cell_surface_hover = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface_hover, line_colour_hover, cell_rect, selected_hover_border_width, 1)

        # Surface for the cell that was selected
        self.cell_surface_selected = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface_selected, line_colour_selected, cell_rect, selected_hover_border_width, 1)

    def _move_unit_to_cell(self, unit: Unit, cell: GridCell):
        cell_center_x, cell_center_y = cell.rect.x + self.cell_size // 2, cell.rect.y + self.cell_size // 2
        cell.unit = unit
        # TODO: fix the following calculation, unit.size is NOT the size of the unit so this is wrong
        unit.set_position([cell_center_x + unit.size // 2, cell_center_y + unit.size // 2])

    def move_units_to_grid(self):
        """
        Moves each unit to the position of a grid cell and assigns a reference to the unit in each cell, so that
        the units can be switched after two of them are selected
        """
        if not self.are_units_aligned_to_grid:
            for i, unit_cell in enumerate(zip(self.units, self.cells)):
                unit, cell = unit_cell
                self._move_unit_to_cell(unit, cell)
            self.are_units_aligned_to_grid = True

    def process_input(self):
        """
        Check if there are changes in mouse position, click or gamepad input and change the selected_cell  and
        hover_cell variables accordingly
        """

        mouse_x, mouse_y = self._game.input.mouse_pos
        clicked = self._game.input.mouse_state["left"]

        cell_x_index, cell_y_index = (int(mouse_x) - self.margin_x) // self.cell_size, (
            int(mouse_y) - self.margin_y
        ) // self.cell_size

        mouse_x_is_out_of_placement_area = cell_x_index < 0 or cell_x_index >= self.cells_x_size
        mouse_y_is_out_of_placement_area = cell_y_index < 0 or cell_y_index >= self.cells_y_size

        if mouse_x_is_out_of_placement_area or mouse_y_is_out_of_placement_area:
            return

        # Converts 2d x and y position to a single position with the index of the cell in the array
        cell = self.cells[cell_y_index * self.cells_x_size + cell_x_index]

        if not clicked:  # Mouse/gamepad is hovering over cell, but it was not selected
            self.hover_cell = cell

        elif not self.selected_cell:  # The current cell was selected and there is no previously selected cell
            self.selected_cell = cell
            cell.unit.is_selected = True

        elif self.selected_cell is cell:  # The cell was unselected by the user
            self.selected_cell = None

        elif self.selected_cell is not cell:  # Two cells were selected, attempt unit position switching
            # Both cells have units, so we switch their positions
            if self.selected_cell.unit and cell.unit:
                selected_unit_pos = self.selected_cell.unit.pos
                self.selected_cell.unit.set_position(cell.unit.pos)
                self.selected_cell.unit.is_selected = False
                cell.unit.set_position(selected_unit_pos)
                cell.unit.is_selected = False

            # Only selected_cell has a unit, so we assign it to cell.unit and set selected_cell's unit to None
            elif self.selected_cell.unit and not cell.unit:
                cell.unit = self.selected_cell.unit
                cell.unit.is_selected = False
                self._move_unit_to_cell(cell.unit, cell)
                self.selected_cell.unit = None

            # Only cell.unit has a unit, so we assign it to selected_cell and set cell's unit to None
            elif cell.unit and not self.selected_cell.unit:
                self.selected_cell.unit = cell.unit
                self.selected_cell.unit.is_selected = False
                self._move_unit_to_cell(self.selected_cell.unit, self.selected_cell)
                cell.unit = None

            self.hover_cell = self.selected_cell = None

    def draw(self, surface: pygame.Surface):
        for i, cell in enumerate(self.cells):
            if cell is self.selected_cell:
                grid_surface = self.cell_surface_selected
            elif cell is self.hover_cell:
                grid_surface = self.cell_surface_hover
            else:
                grid_surface = self.cell_surface
            surface.blit(grid_surface, cell.rect)

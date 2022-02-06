from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, SceneType, WorldState
from scripts.scene_elements.unit import Unit
from scripts.scene_elements.world.view import WorldView
from scripts.ui_elements.frame import Frame

if TYPE_CHECKING:
    from scripts.core.game import Game
    from typing import List, Optional
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
        self._victory_duration: float = 0.0
        self.grid: Optional[UnitGrid] = None

    def update(self, delta_time: float):
        self._worldview.update(delta_time)

        # need to call here as otherwise units dont align to grid
        # TODO - fix need to call after init
        if self.grid is None:
            self.grid = UnitGrid(self._game)
            self.grid.move_units_to_grid()

        if self._parent_scene.model.state == WorldState.COMBAT_VICTORY:
            self._victory_duration += delta_time
            if self._victory_duration >= 3:
                self.rebuild_ui()

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # TODO  - replace when new room choice is in.
        if self._parent_scene.model.state == WorldState.IDLE:
            if self._game.input.states["backspace"]:
                self._parent_scene.combat.begin_move_to_new_room()

        # manual camera control for debugging
        # if self._game.input.states["up"]:
        #     self._game.input.states["up"] = False
        #     self._worldview.camera.move(y=-32)
        # if self._game.input.states["down"]:
        #     self._game.input.states["down"] = False
        #     self._worldview.camera.move(y=32)
        # if self._game.input.states["left"]:
        #     self._game.input.states["left"] = False
        #     self._worldview.camera.move(x=-32)
        # if self._game.input.states["right"]:
        #     self._game.input.states["right"] = False
        #     self._worldview.camera.move(x=32)

        #############################################

        if self._parent_scene.model.state == WorldState.DEFEAT:
            if self._game.input.states["select"]:
                self._game.memory.reset()
                self._game.change_scene(SceneType.MAIN_MENU)

        if self.grid:
            self.grid.process_input()

    def draw(self, surface: pygame.Surface):
        self._worldview.draw(surface)

        # TODO: create and move to mouse tool system
        if self._parent_scene.model.state == WorldState.IDLE:
            if self.grid:
                self.grid.draw(surface)

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        create_font = self._game.assets.create_font

        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x = self._game.window.centre[0]
        start_y = self._game.window.centre[1]

        # draw upgrades
        current_x = start_x
        current_y = start_y

        if self._parent_scene.model.state == WorldState.DEFEAT:
            defeat_icon = self._game.assets.get_image("ui", "arrow_button", icon_size)
            frame = Frame(
                (current_x, current_y),
                image=defeat_icon,
                font=create_font(FontType.NEGATIVE, "Defeated"),
                is_selectable=False,
            )
            self._elements["defeat_notification"] = frame

            current_y += 100

            frame = Frame(
                (current_x, current_y),
                image=defeat_icon,
                font=create_font(FontType.DEFAULT, "Press Enter to return to the main menu."),
                is_selectable=False,
            )
            self._elements["defeat_instruction"] = frame

        if self._parent_scene.model.state == WorldState.COMBAT_VICTORY:
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

        cell_x_index, cell_y_index = (int(mouse_x) - self.margin_x) // self.cell_size, \
            (int(mouse_y) - self.margin_y) // self.cell_size

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

        elif self.selected_cell is cell:  # The cell was unselected by the user
            self.selected_cell = None

        elif self.selected_cell is not cell:  # Two cells were selected, attempt unit position switching
            # Both cells have units, so we switch their positions
            if self.selected_cell.unit and cell.unit:
                selected_unit_pos = self.selected_cell.unit.pos
                self.selected_cell.unit.set_position(cell.unit.pos)
                cell.unit.set_position(selected_unit_pos)

            # Only selected_cell has a unit, so we assign it to cell.unit and set selected_cell's unit to None
            elif self.selected_cell.unit and not cell.unit:
                cell.unit = self.selected_cell.unit
                self._move_unit_to_cell(cell.unit, cell)
                self.selected_cell.unit = None

            # Only cell.unit has a unit, so we assign it to selected_cell and set cell's unit to None
            elif cell.unit and not self.selected_cell.unit:
                self.selected_cell.unit = cell.unit
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

from __future__ import annotations

from typing import List, Optional

import pygame

from scripts.core.constants import TILE_SIZE, InputType
from scripts.core.game import Game
from scripts.core.grid import grid_up, grid_down, grid_left, grid_right
from scripts.scene_elements.unit import Unit


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

    Args:
        game: Game object
        rect: Rect of grid in tile size

    """

    def __init__(self, game: Game, rect: pygame.Rect):
        # TODO:
        #  - show units moving on screen instead of setting their positions
        #  - there's still a bug somewhere that keeps units from switching placement
        self._game: Game = game
        self.rect: pygame.Rect = rect
        # TODO: scale value needs to come from the View somewhere
        scale = 2
        self.cell_size: int = TILE_SIZE * scale
        # Pixel border of each cell
        self.cell_border_width: int = 1
        self.focused_border_width: int = 3
        # Number of vertical and horizontal cells
        # Troupe units for placement
        self.units: List[Unit] = game.world.model.get_all_units()
        self.are_units_aligned_to_grid = False
        self.selected_cell = None
        self.focused_cell = None
        self.cells: List[GridCell] = list()
        self.cell_surface: pygame.Surface = None
        self.cell_surface_hover: pygame.Surface = None
        self.cell_surface_selected: pygame.Surface = None
        self.line_colour = (0, 100, 0)
        self.line_colour_hover = (0, 140, 0)
        self.line_colour_selected = (0, 180, 0)
        self._interaction_owner: InputType = InputType.NONE
        self._previous_focused: Optional[GridCell] = None
        self.initialize_cells()

    def initialize_cells(self):
        """
        Initializes grid cells

        """

        size_border = self.cell_size + (self.cell_border_width * 2)
        size_internal = self.cell_size + self.cell_border_width
        width = (self.rect.width * size_internal) + self.cell_border_width
        height = (self.rect.height * size_internal) + self.cell_border_width
        cell_rect = pygame.Rect((0, 0), (size_border, size_border))

        top = self.rect.y * self.cell_size
        right = self.rect.x * self.cell_size

        self.cells = [
            GridCell(pygame.Rect((x + right, y + top), cell_rect.size))
            for y in range(self.cell_border_width, height, size_internal)
            for x in range(self.cell_border_width, width, size_internal)
        ]

        # Surface for cells that were not selected, under current mouse position or gamepad selection
        self.cell_surface = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface, self.line_colour, cell_rect, 1)

        # Surface for the cell that's under the current mouse position or gamepad selection, but not selected
        self.cell_surface_hover = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface_hover, self.line_colour_hover, cell_rect, self.focused_border_width)

        # Surface for the cell that was selected
        self.cell_surface_selected = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface_selected, self.line_colour_selected, cell_rect, self.focused_border_width)

    def _move_unit_to_cell(self, unit: Unit, cell: GridCell):
        """
        Instantly move unit to cell

        """
        cell_center_x, cell_center_y = cell.rect.x + self.cell_size // 2, cell.rect.y + self.cell_size // 2
        cell.unit = unit
        # # TODO: fix the following calculation, unit.size is NOT the size of the unit so this is wrong
        unit.set_position([cell_center_x + unit.size // 2, cell_center_y + unit.size // 2])

    def _walk_unit_to_cell(self, unit: Unit, cell: GridCell):
        """
        Move unit to cell by setting the entities on a path

        """
        # this logic could be replaced by
        # - pathfinding leader to the cell
        # - making the others follow the leader
        target = cell.rect.center
        cell.unit = unit
        unit.forced_behaviour = True
        leader = unit.entities[0]
        leader.behaviour.current_path = [target]
        leader.behaviour.state = "path_fast"
        for entity in unit.entities[1:]:
            entity.behaviour.current_path = [target]
            entity.behaviour.state = "path_fast"

    def move_units_to_grid(self):
        """
        Moves each unit to the position of a grid cell and assigns a
        reference to the unit in each cell, so that the units can be
        switched after two of them are selected.

        """
        if not self.are_units_aligned_to_grid:
            for i, unit_cell in enumerate(zip(self.units, self.cells)):
                unit, cell = unit_cell
                self._move_unit_to_cell(unit, cell)
            self.are_units_aligned_to_grid = True

    def process_input(self):
        """
        Check if there are changes in mouse position, click or gamepad
        input and change the selected_cell and hover_cell variables accordingly

        """
        if self.focused_cell:
            self._previous_focused = self.focused_cell
        self.focused_cell = focused = self.get_focused_cell()

        if focused is None:
            return

        clicked = self._game.input.mouse_state["left"] or self._game.input.states["select"]
        self._game.input.states["select"] = False

        # Mouse/gamepad is hovering over cell, but it was not selected
        if not clicked:
            self.focused_cell = focused

        # The current cell was selected and there is no previously selected cell
        elif not self.selected_cell:
            self.selected_cell = focused
            if focused.unit:
                focused.unit.is_selected = True

        # The cell was unselected by the user
        elif self.selected_cell is focused:
            self.selected_cell = None

        # Two cells were selected, attempt unit position switching
        elif self.selected_cell is not focused:
            # Both cells have units, so we switch their positions
            if self.selected_cell.unit and focused.unit:
                selected_unit_pos = self.selected_cell.unit.pos
                # self.selected_cell.unit.set_position(focused.unit.pos)
                self.selected_cell.unit.is_selected = False
                # focused.unit.set_position(selected_unit_pos)
                focused.unit.is_selected = False
                self._walk_unit_to_cell(self.selected_cell.unit, focused.unit.pos)
                self._walk_unit_to_cell(focused.unit, selected_unit_pos)

            # Only selected_cell has a unit, so we assign it to cell.unit and set selected_cell's unit to None
            elif self.selected_cell.unit and not focused.unit:
                focused.unit = self.selected_cell.unit
                focused.unit.is_selected = False
                self._walk_unit_to_cell(focused.unit, focused)
                self.selected_cell.unit = None

            # Only cell.unit has a unit, so we assign it to selected_cell and set cell's unit to None
            elif focused.unit and not self.selected_cell.unit:
                self.selected_cell.unit = focused.unit
                self.selected_cell.unit.is_selected = False
                self._walk_unit_to_cell(self.selected_cell.unit, self.selected_cell)
                focused.unit = None

            if self._interaction_owner == InputType.MOUSE:
                self.focused_cell = self.selected_cell = None
            else:
                self.selected_cell = None

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2):
        # NOTE: awkward sort because the selected/hovered cell must be drawn last
        draw_list = list()
        for i, cell in enumerate(self.cells):
            if cell is self.selected_cell:
                draw_list.append((2, i, cell, self.cell_surface_selected))
            elif cell is self.focused_cell:
                draw_list.append((1, i, cell, self.cell_surface_hover))
            else:
                draw_list.append((0, i, cell, self.cell_surface))
        draw_list.sort()
        for rank, index, cell, cell_surface in draw_list:
            surface.blit(cell_surface, offset + cell.rect.topleft)

    def get_focused_cell(self) -> Optional[GridCell]:
        """
        Return the current focused cell after input processing

        The return value may be the same as the current focused cell

        """
        focused = None

        if self._game.input.mouse_moved:
            focused = self.get_mouse_hovered_cell()
            if focused is None:
                if self._interaction_owner is InputType.MOUSE:
                    # player moved mouse off the grid; no longer focused
                    return None
            else:
                self._interaction_owner = InputType.MOUSE

        if focused is None:
            focused = self.handle_keys()

        if focused is None:
            # no change in focus, so return the existing one, if any
            return self.focused_cell
        else:
            return focused

    def get_mouse_hovered_cell(self) -> Optional[GridCell]:
        """
        Return the GridCell object mouse is over, if any

        """
        # TODO: cleanup this reference
        view = self._game.world.ui._worldview
        mouse = view.view_to_point(self._game.input.mouse_pos)

        for cell in self.cells:
            if cell.rect.collidepoint(mouse):
                return cell

    def handle_keys(self) -> Optional[GridCell]:
        """
        Return GridCell object after processing keys, if any

        """
        direction_handlers = (
            ("up", grid_up),
            ("down", grid_down),
            ("left", grid_left),
            ("right", grid_right),
        )
        hover_cell = None
        handled_movement = False
        for direction, movement in direction_handlers:
            if self._game.input.states[direction]:
                self._game.input.states[direction] = False
                if not handled_movement:
                    handled_movement = True
                    self._interaction_owner = InputType.KEYS
                    if self.focused_cell is None:
                        if self._previous_focused is not None:
                            index = self.cells.index(self._previous_focused)
                        else:
                            index = 0
                        hover_cell = self.cells[index]
                    else:
                        index = self.cells.index(self.focused_cell)
                        new_index = movement(index, self.rect.width, self.rect.height)
                        hover_cell = self.cells[new_index]
        return hover_cell

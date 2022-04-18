from __future__ import annotations

from typing import List, Optional

import pygame
import snecs

from nqp.command.unit import Unit
from nqp.core.components import AI
from nqp.core.constants import InputType, TILE_SIZE
from nqp.core.game import Game
from nqp.core.utility import grid_down, grid_left, grid_right, grid_up


class GridCell:
    """
    A representation of the smallest discrete space in a Grid.

    """

    def __init__(self, rect: pygame.Rect, unit: Unit = None):
        self.rect: pygame.Rect = rect
        self.unit: Unit | None = unit


class UnitGrid:
    """
    An organised layout of rows and columns for Unit placement.

    Args:
        game: Game object
        pos: Position of the grid in tile coordinates
        size: size of the grid in cell_size units
        scale: amount to scale the TILE_SIZE to get cell_size units

    """

    def __init__(self, game: Game, pos, size, scale: int):
        # TODO - there's still a bug somewhere that keeps units from switching placement
        self._game: Game = game
        self.pos: pygame.Vector2 = pygame.Vector2(pos)
        self.size: pygame.Vector2 = pygame.Vector2(size)
        self.scale: int = scale
        self.cell_size: int = int(scale * TILE_SIZE)
        # Pixel border of each cell
        self.cell_border_width: int = 1
        self.focused_border_width: int = 3
        self.units: List[Unit] = game.world.model.get_all_units()
        self.are_units_aligned_to_grid = False
        self.selected_cell: Optional[GridCell] = None
        self.focused_cell: Optional[GridCell] = None
        self.cells: List[GridCell] = list()
        self.cell_surface: Optional[pygame.Surface] = None
        self.cell_surface_hover: Optional[pygame.Surface] = None
        self.cell_surface_selected: Optional[pygame.Surface] = None
        self.line_colour = (0, 100, 0)
        self.line_colour_hover = (0, 140, 0)
        self.line_colour_selected = (0, 180, 0)
        self._interaction_owner: InputType = InputType.NONE
        self._previous_focused: Optional[GridCell] = None
        self.initialize_cells()

        # set focus to first cell
        self.focused_cell = self.cells[0]

    def initialize_cells(self):
        """
        Initializes grid cells and graphics

        """
        cell_rect = pygame.Rect((0, 0), (self.cell_size, self.cell_size))
        left = int(self.pos.x * TILE_SIZE)
        top = int(self.pos.y * TILE_SIZE)

        self.cells = [
            GridCell(pygame.Rect((x + left, y + top), cell_rect.size))
            for y in range(0, int(self.size.y * self.cell_size), self.cell_size)
            for x in range(0, int(self.size.x * self.cell_size), self.cell_size)
        ]

        # Surface for cells that were not selected, under current mouse position or gamepad selection
        self.cell_surface = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
        self.cell_surface.fill((32, 32, 32, 32))

        # Surface for the cell that's under the current mouse position or gamepad selection, but not selected
        self.cell_surface_hover = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface_hover, self.line_colour_hover, cell_rect, self.focused_border_width, 3)
        erase = cell_rect.x + (cell_rect.width * 0.15), cell_rect.y, cell_rect.width * 0.75, cell_rect.height
        self.cell_surface_hover.fill((0, 0, 0, 0), erase)

        # Surface for the cell that was selected
        self.cell_surface_selected = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.cell_surface_selected, self.line_colour_selected, cell_rect, self.focused_border_width)

    def _move_unit_to_cell(self, unit: Unit, cell: GridCell):
        """
        Instantly move unit to cell

        """
        cell_center = pygame.Vector2(cell.rect.center)
        cell.unit = unit
        # TODO: fix the following calculation, unit.size is NOT the size of the unit so this is wrong
        # unit.set_position(pygame.Vector2(cell_center.x + unit.size // 2, cell_center.y + unit.size // 2))
        unit.set_position(cell_center)

    def _walk_cell_to_cell(self, unit: Unit, dest: GridCell):
        """
        Move unit to cell by setting the entities on a path

        ** This does not change the unit attribute of the cell **

        """
        # this logic could be replaced by
        # - pathfinding leader to the cell
        # - making the others follow the leader
        unit.forced_behaviour = True
        target_px = dest.rect.center
        leader = unit.behaviour.leader
        leader_behaviour = snecs.entity_component(leader, AI).behaviour
        leader_behaviour.current_path = [target_px]
        leader_behaviour.state = "path_fast"
        for entity in unit.entities[1:]:
            behaviour = snecs.entity_component(entity, AI).behaviour
            behaviour.current_path = [target_px]
            behaviour.state = "path_fast"

    def _swap_cells(self, a: GridCell, b: GridCell):
        """
        Swap the units between two cells

        Can swap empty cells with filled cells

        """
        if a.unit:
            self._walk_cell_to_cell(a.unit, b)
        if b.unit:
            self._walk_cell_to_cell(b.unit, a)
        a_unit = a.unit
        a.unit = b.unit
        b.unit = a_unit

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

    def move_to_empty_cell(self, unit: Unit):
        for cell in self._game.world.ui.grid.cells:
            if cell.unit is None:
                cell.unit = unit
                unit.forced_behaviour = True
                target_px = cell.rect.center
                leader = unit.entities[0]
                behaviour = snecs.entity_component(leader, AI).behaviour
                behaviour.current_path = [target_px]
                behaviour.state = "path_fast"

                for entity in unit.entities[1:]:
                    behaviour = snecs.entity_component(entity, AI).behaviour
                    behaviour.current_path = [target_px]
                    behaviour.state = "path_fast"
                break

    def process_input(self):
        """
        Logic for gampad/mouse input to move units in grid

        """
        if self.focused_cell:
            self._previous_focused = self.focused_cell
        self.focused_cell = focused_cell = self.get_focused_cell()

        if focused_cell is None:
            return

        clicked = self._game.input.mouse_state["left"] or self._game.input.states["select"]
        self._game.input.states["select"] = False

        if clicked:
            # There is no previously selected cell
            if not self.selected_cell:
                self.selected_cell = focused_cell

            # The same cell was selected twice, so unselect it
            elif self.selected_cell is focused_cell:
                self.selected_cell = None
                if self._interaction_owner == InputType.MOUSE:
                    if focused_cell.unit:
                        focused_cell.unit.is_selected = False

            # Two cells were selected, attempt unit position switching
            else:
                self._swap_cells(self.selected_cell, focused_cell)
                if focused_cell.unit:
                    focused_cell.unit.is_selected = False
                if self.selected_cell.unit:
                    self.selected_cell.unit.is_selected = False
                self.selected_cell = None
                if self._interaction_owner == InputType.MOUSE:
                    self.focused_cell = None

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2):
        """
        Draw the grid UI elements

        """
        # draw grid lines
        left = int(self.pos.x * TILE_SIZE - self.cell_border_width + offset.x)
        top = int(self.pos.y * TILE_SIZE - self.cell_border_width + offset.y)
        width = int(self.size.x * self.cell_size)
        height = int(self.size.y * self.cell_size)
        bottom = top + height
        right = left + width
        pygame.draw.lines(surface, self.line_colour, False, ((left, bottom), (left, top), (right, top)), 1)
        for x in range(left, right + 1, self.cell_size):
            pygame.draw.line(surface, self.line_colour, (x, top), (x, bottom))
        for y in range(top, bottom + 1, self.cell_size):
            pygame.draw.line(surface, self.line_colour, (left, y), (right, y))

        # NOTE: awkward sort because the selected/hovered cell must be drawn last
        draw_list = list()
        for i, cell in enumerate(self.cells):
            unmodified = True
            if cell is self.focused_cell:
                draw_list.append((2, i, cell, self.cell_surface_hover))
                unmodified = False
            if cell is self.selected_cell:
                draw_list.append((1, i, cell, self.cell_surface_selected))
                unmodified = False
            if unmodified:
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
                        new_index = movement(index, int(self.size.x), int(self.size.y))
                        hover_cell = self.cells[new_index]
        return hover_cell

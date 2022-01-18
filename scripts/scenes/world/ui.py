from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import FontType, WorldState
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.terrain import Terrain
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game
    from scripts.scenes.world.scene import WorldScene


__all__ = ["WorldUI"]


######### TO DO LIST ###############


class WorldUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, parent_scene: WorldScene):
        super().__init__(game, False)
        self.parent_scene: WorldScene = parent_scene

        # TODO - info pulled over from combat to render terrain, needs clean up
        self.camera: Camera = Camera()
        self.terrain: Terrain = Terrain(self.game)
        self.biome = "plains"
        self.mod_delta_time = 0  # actual delta time by combat speed
        self.combat_speed = 1
        self.force_idle = False
        self.grid = None

    def update(self, delta_time: float):
        super().update(delta_time)

        self.mod_delta_time = self.combat_speed * delta_time

        if not self.force_idle:
            self.terrain.update(self.mod_delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # TODO  - replace when new room choice is in.
        if self.game.input.states["backspace"]:
            self.parent_scene.move_to_new_room()

        if self.grid:
            self.grid.process_input()

    def render(self, surface: pygame.Surface):
        self.camera.bind(self.terrain.boundaries)
        combat_surf = pygame.Surface(self.game.window.display.get_size())  # Not sure we need this?
        self.terrain.render(combat_surf, self.camera.render_offset())

        if self.parent_scene.state == WorldState.IDLE:
            self.parent_scene.unit_manager.render(combat_surf, self.camera.render_offset())

        # blit the terrain and unit_manager
        self.game.window.display.blit(
            combat_surf,
            (
                -(combat_surf.get_width() - self.game.window.display.get_width()) // 2,
                -(combat_surf.get_height() - self.game.window.display.get_height()) // 2,
            ),
        )

        if not self.grid:
            """
            Initializes grid object. It's not done on init because the grid depends on parent_scene objects that are not
            yet initialized by the time init is called
            """
            self.grid = Grid(self.parent_scene, surface)
            self.grid.move_units_to_grid()

        self.grid.render()

        self.draw_instruction(surface)
        self.draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        self.terrain.generate(self.biome)


class GridCell:
    def __init__(self, rect: pygame.Rect, unit: Unit = None):
        self.rect = rect
        self.unit = unit


class Grid:
    def __init__(self, parent_scene: WorldScene, surface: pygame.Surface):
        self.cell_size = parent_scene.grid_cell_size  # Size of each cell
        self.cells_x_size, self.cells_y_size = parent_scene.grid_size  # Number of vertical and horizontal cells
        self.units: List[Unit] = parent_scene.unit_manager.units  # Troupe units for placement
        self.game = parent_scene.game
        # TODO:
        #  - get margin from parent_scene
        #  - check if there are unnecessary variables/functions related to grid in world/scene.py
        #  - get the grid to move with the camera
        #  - support gamepad
        #  - show units moving on screen instead of setting their positions
        #  - there's still a bug somewhere that keeps units from switching placement
        self.margin_x, self.margin_y = 16 * 5, 16 * 6
        self.surface = surface
        self.moved_units_to_grid = False
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

    def move_unit_to_cell(self, unit: Unit, cell: GridCell):
        cell_center_x, cell_center_y = cell.rect.x + self.cell_size // 2, cell.rect.y + self.cell_size // 2
        cell.unit = unit
        # TODO: fix the following calculation, unit.size is NOT the size of the unit so this is wrong
        unit.set_position([cell_center_x + unit.size // 2, cell_center_y + unit.size // 2])

    def move_units_to_grid(self):
        """
        Moves each unit to the position of a grid cell and assigns a reference to the unit in each cell, so that
        the units can be switched after two of them are selected
        """
        if not self.moved_units_to_grid:
            for i, unit_cell in enumerate(zip(self.units, self.cells)):
                unit, cell = unit_cell
                self.move_unit_to_cell(unit, cell)
            self.moved_units_to_grid = True

    def process_input(self):
        """
        Check if there are changes in mouse position, click or gamepad input and change the selected_cell and hover_cell
        variables accordingly
        """

        mouse_x, mouse_y = self.game.input.mouse_pos
        clicked = self.game.input.mouse_state["left"]

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
                self.move_unit_to_cell(cell.unit, cell)
                self.selected_cell.unit = None

            # Only cell.unit has a unit, so we assign it to selected_cell and set cell's unit to None
            elif cell.unit and not self.selected_cell.unit:
                self.selected_cell.unit = cell.unit
                self.move_unit_to_cell(self.selected_cell.unit, self.selected_cell)
                cell.unit = None

            self.hover_cell = self.selected_cell = None

    def render(self):
        for i, cell in enumerate(self.cells):
            if cell is self.selected_cell:
                surface = self.cell_surface_selected
            elif cell is self.hover_cell:
                surface = self.cell_surface_hover
            else:
                surface = self.cell_surface
            self.surface.blit(surface, cell.rect)

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, SceneType, WorldState
from scripts.scene_elements.world.view import WorldView
from scripts.ui_elements.frame import Frame

if TYPE_CHECKING:
    from scripts.core.game import Game
    from scripts.scene_elements.world.model import WorldModel
    from scripts.scenes.world.combat import CombatController


__all__ = ["WorldUI"]


class WorldUI(UI):
    """
    Represent the UI of the WorldScene

    """

    def __init__(
        self,
        game: Game,
        model: WorldModel,
        controller: CombatController,
    ):
        super().__init__(game, False)
        self._model = model
        self._controller = controller
        self._worldview = WorldView(game, model)
        self._victory_duration: float = 0.0

    def update(self, delta_time: float):
        self._worldview.update(delta_time)

        if self._controller.state == WorldState.COMBAT_VICTORY:
            self._victory_duration += delta_time
            if self._victory_duration >= 3:
                self.rebuild_ui()

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # TODO  - replace when new room choice is in.
        if self._controller.state == WorldState.IDLE:
            if self._game.input.states["backspace"]:
                self._controller.move_to_new_room()
            if self._game.input.states["select"]:
                self._controller.state = WorldState.COMBAT
                for troupe in self._game.memory.troupes.values():
                    troupe.set_force_idle(False)

        if self._game.input.states["up"]:
            self._game.input.states["up"] = False
            self._worldview.camera.move(y=-32)
        if self._game.input.states["down"]:
            self._game.input.states["down"] = False
            self._worldview.camera.move(y=32)
        if self._game.input.states["left"]:
            self._game.input.states["left"] = False
            self._worldview.camera.move(x=-32)
        if self._game.input.states["right"]:
            self._game.input.states["right"] = False
            self._worldview.camera.move(x=32)

        #############################################

        if self._controller.state == WorldState.DEFEAT:
            if self._game.input.states["select"]:
                self._game.memory.reset()
                self._game.change_scene(SceneType.MAIN_MENU)

    def draw(self, surface: pygame.Surface):
        self._worldview.draw(surface)

        # TODO: create and move to mouse tool system
        if self._controller.state == WorldState.IDLE:
            self._draw_grid(surface)

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

        if self._controller.state == WorldState.DEFEAT:
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

        if self._controller.state == WorldState.COMBAT_VICTORY:
            frame = Frame(
                (current_x, current_y),
                font=create_font(FontType.POSITIVE, "Victory"),
                is_selectable=False,
            )
            self._elements["victory_notification"] = frame

    def _draw_grid(self, surface: pygame.Surface):
        """
        Draw the unit selection grid
        """
        grid_size = self._model.grid_size
        grid_cell_size = self._model.grid_cell_size
        grid_margin = self._model.grid_margin
        line_colour = (0, 0, 0)

        # draw horizontal lines
        for h_line in range(grid_size[1] + 1):
            start_x = grid_margin
            start_y = h_line * grid_cell_size + grid_margin
            end_x = grid_size[0] * grid_cell_size + grid_margin
            end_y = h_line * grid_cell_size + grid_margin
            pygame.draw.line(surface, line_colour, (start_x, start_y), (end_x, end_y))

        # draw vertical lines
        for v_line in range(grid_size[0] + 1):
            start_x = v_line * grid_cell_size + grid_margin
            start_y = grid_margin
            end_x = v_line * grid_cell_size + grid_margin
            end_y = grid_size[1] * grid_cell_size + grid_margin
            pygame.draw.line(surface, line_colour, (start_x, start_y), (end_x, end_y))

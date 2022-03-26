from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    import pygame

    from scripts.core.base_classes.scene import Scene
    from scripts.core.game import Game
    from scripts.ui_elements.font import Font
    from scripts.ui_elements.unit_stats_window import UnitStatsFrame


__all__ = ["UI"]


######### TO DO LIST ###############


class UI(ABC):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, block_onward_input: bool):
        self._game: Game = game
        self.block_onward_input: bool = block_onward_input  # prevents input being passed to the next scene

        self._elements: Dict[str, Union[Frame, UnitStatsFrame]] = {}
        self._panels: Dict[str, Panel] = {}
        self._current_panel: Optional[Panel] = None

        self._temporary_instruction_text: str = ""
        self._temporary_instruction_timer: float = 0.0
        self._instruction_text: str = ""

        self.is_active: bool = False

    def update(self, delta_time: float):
        self._temporary_instruction_timer -= delta_time

        if self._temporary_instruction_timer <= 0:
            self._temporary_instruction_text = ""

        self.update_elements(delta_time)

    def process_input(self, delta_time: float):
        if self._game.input.states["toggle_dev_console"]:
            self._game.input.states["toggle_dev_console"] = False

            self._game.debug.toggle_dev_console_visibility()

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    def rebuild_ui(self):
        self._elements = {}
        self._panels = {}

    def activate(self):
        """
        Activate the UI. Rebuilds and begins rendering the UI.
        """
        self.rebuild_ui()
        self.is_active = True

    def deactivate(self):
        """
        Deactivate the UI. R
        """
        self.is_active = False

    def refresh_info(self):
        pass

    def set_instruction_text(self, text: str, temporary: bool = False):
        if temporary:
            self._temporary_instruction_text = text
            self._temporary_instruction_timer = 2
        else:
            self._instruction_text = text

    def rebuild_resource_elements(self):
        """
        Build Panel and Frames for key resources on screen. Gold, Rations, Charisma, Leadership.
        """
        # TODO - resources now in WorldModel, this needs to be moved to somewhere that can access that.
        icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        # specify resources
        # key : [value, icon]
        resources = {
            "gold": [
                self._game.assets.get_image("stats", "gold", icon_size),
                str(self._game.memory.gold),
            ],
            "rations": [
                self._game.assets.get_image("stats", "rations", icon_size),
                str(self._game.memory.rations),
            ],
            "morale": [
                self._game.assets.get_image("stats", "morale", icon_size),
                str(self._game.memory.morale),
            ],
            "charisma": [
                self._game.assets.get_image("stats", "charisma", icon_size),
                str(self._game.memory.commander.charisma_remaining),
            ],
            "leadership": [
                self._game.assets.get_image("stats", "leadership", icon_size),
                str(self._game.memory.leadership),
            ],
        }

        panel_elements = []

        # positions
        start_x = 2
        start_y = 2
        current_x = start_x
        current_y = start_y

        # create frames
        create_font = self._game.assets.create_font
        for key, value in resources.items():
            frame = Frame(
                self._game,
                (current_x, current_y),
                image=value[0],
                font=create_font(FontType.DISABLED, value[1]),
                is_selectable=False,
            )
            self._elements[f"resource_{key}"] = frame
            panel_elements.append(frame)

            # increment position
            current_x += frame.width + GAP_SIZE

        # create panel
        panel = Panel(self._game, panel_elements, True)
        panel.unselect_all_elements()
        self._panels["resources"] = panel

    def _draw_instruction(self, surface: pygame.Surface):
        if self._temporary_instruction_text:
            text = self._temporary_instruction_text
            font = self._game.assets.create_font(FontType.NEGATIVE, text)
        else:
            text = self._instruction_text
            font = font = self._game.assets.create_font(FontType.INSTRUCTION, text)

        x = self._game.window.width - font.width - 2
        y = 2
        font.pos = (x, y)
        font.draw(surface)

    def _draw_elements(self, surface: pygame.Surface):
        for name, element in self._elements.items():
            element.draw(surface)

    def update_elements(self, delta_time: float):
        for element in self._elements.values():
            element.update(delta_time)

    def add_panel(self, panel: Panel, name: str):
        """
        Adds panel to the panel dict. If it is the first panel then also sets it to the current panel and selects the
         first element.
        """
        self._panels[name] = panel

        if len(self._panels) == 1:
            self._current_panel = self._panels[name]
            self._current_panel.select_first_element()

    def add_exit_button(self, button_text: str = "Onwards") -> Panel:
        """
        Add an exit button to the ui. Returns the panel containing the exit button.
        """
        window_width = self._game.window.width
        window_height = self._game.window.height
        font = self._game.assets.create_font(FontType.DEFAULT, button_text)

        # get position info
        confirm_width = font.get_text_width(button_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (font.line_height + GAP_SIZE)

        frame = Frame(self._game, (current_x, current_y), font=font, is_selectable=True)
        self._elements["exit"] = frame
        panel = Panel(self._game, [frame], True)
        self.add_panel(panel, "exit")

        return panel

    def select_panel(self, panel_name: str, hide_old_panel: bool = False):
        """
        Unselect the current panel and move the selection to the specified panel.
        """
        # unselect current
        self._current_panel.unselect_all_elements()

        if hide_old_panel:
            self._current_panel._is_active = False

        # select new
        try:
            self._current_panel = self._panels[panel_name]

        except KeyError:
            logging.critical(
                f"Tried to change to {panel_name} panel, but does not exist. Selected first panel " f"instead."
            )
            self._current_panel = list(self._panels)[0]

        self._current_panel.select_first_element()
        self._current_panel._is_active = True

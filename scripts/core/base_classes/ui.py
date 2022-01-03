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

    from scripts.core.game import Game
    from scripts.ui_elements.font import Font
    from scripts.ui_elements.unit_stats_frame import UnitStatsFrame
    from scripts.core.base_classes.scene import Scene


__all__ = ["UI"]


######### TO DO LIST ###############


class UI(ABC):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game, parent_scene: Scene, block_onward_input: bool):
        self.game: Game = game
        self.parent_scene: Scene = parent_scene
        self.block_onward_input: bool = block_onward_input  # prevents input being passed to the next scene

        self.elements: Dict[str, Union[Frame, UnitStatsFrame]] = {}
        self.panels: Dict[str, Panel] = {}
        self.current_panel: Optional[Panel] = None

        self.temporary_instruction_text: str = ""
        self.temporary_instruction_timer: float = 0.0
        self.instruction_text: str = ""

    def update(self, delta_time: float):
        self.temporary_instruction_timer -= delta_time

        if self.temporary_instruction_timer <= 0:
            self.temporary_instruction_text = ""

        self.update_elements(delta_time)

    def process_input(self, delta_time: float):
        if self.game.input.states["toggle_dev_console"]:
            self.game.input.states["toggle_dev_console"] = False

            self.game.debug.toggle_dev_console_visibility()

    @abstractmethod
    def render(self, surface: pygame.surface):
        pass

    def rebuild_ui(self):
        self.elements = {}
        self.panels = {}

    def refresh_info(self):
        pass

    def set_instruction_text(self, text: str, temporary: bool = False):
        if temporary:
            self.temporary_instruction_text = text
            self.temporary_instruction_timer = 2
        else:
            self.instruction_text = text

    def rebuild_resource_elements(self):
        """
        Build Panel and Frames for key resources on screen. Gold, Rations, Charisma, Leadership.
        """
        icon_size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        # specify resources
        # key : [value, icon]
        resources = {
            "gold": [
                self.game.assets.get_image("stats", "gold", icon_size),
                str(self.game.memory.gold),
            ],
            "rations": [
                self.game.assets.get_image("stats", "rations", icon_size),
                str(self.game.memory.rations),
            ],
            "morale": [
                self.game.assets.get_image("stats", "morale", icon_size),
                str(self.game.memory.morale),
            ],
            "charisma": [
                self.game.assets.get_image("stats", "charisma", icon_size),
                str(self.game.memory.commander.charisma_remaining),
            ],
            "leadership": [
                self.game.assets.get_image("stats", "leadership", icon_size),
                str(self.game.memory.leadership),
            ],
        }

        panel_elements = []

        # positions
        start_x = 2
        start_y = 2
        current_x = start_x
        current_y = start_y

        # create frames
        create_font = self.game.assets.create_font
        for key, value in resources.items():
            frame = Frame(
                (current_x, current_y),
                image=value[0],
                font=create_font(FontType.DISABLED, value[1]),
                is_selectable=False,
            )
            self.elements[f"resource_{key}"] = frame
            panel_elements.append(frame)

            # increment position
            current_x += frame.width + GAP_SIZE

        # create panel
        panel = Panel(panel_elements, True)
        panel.unselect_all_elements()
        self.panels["resources"] = panel

    def draw_instruction(self, surface: pygame.surface):
        if self.temporary_instruction_text:
            text = self.temporary_instruction_text
            font = self.game.assets.create_font(FontType.NEGATIVE, text)
        else:
            text = self.instruction_text
            font = font = self.game.assets.create_font(FontType.INSTRUCTION, text)

        x = self.game.window.width - font.width - 2
        y = 2
        font.pos = (x, y)
        font.render(surface)

    def draw_elements(self, surface: pygame.surface):
        for name, element in self.elements.items():
            element.render(surface)

    def update_elements(self, delta_time: float):
        for element in self.elements.values():
            element.update(delta_time)

    def add_panel(self, panel: Panel, name: str):
        """
        Adds panel to the panel dict. If it is the first panel then also sets it to the current panel and selects the
         first element.
        """
        self.panels[name] = panel

        if len(self.panels) == 1:
            self.current_panel = self.panels[name]
            self.current_panel.select_first_element()

    def add_exit_button(self, button_text: str = "Onwards"):
        window_width = self.game.window.width
        window_height = self.game.window.height
        font = self.game.assets.create_font(FontType.DEFAULT, button_text)

        # get position info
        confirm_width = font.get_text_width(button_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (font.line_height + GAP_SIZE)

        frame = Frame((current_x, current_y), font=font, is_selectable=True)
        self.elements["exit"] = frame
        panel = Panel([frame], True)
        self.add_panel(panel, "exit")

    def select_panel(self, panel_name: str, hide_old_panel: bool = False):
        """
        Unselect the current panel and move the selection to the specified panel.
        """
        # unselect current
        self.current_panel.unselect_all_elements()

        if hide_old_panel:
            self.current_panel.is_active = False

        # select new
        try:
            self.current_panel = self.panels[panel_name]

        except KeyError:
            logging.critical(
                f"Tried to change to {panel_name} panel, but does not exist. Selected first panel " f"instead."
            )
            self.current_panel = list(self.panels)[0]

        self.current_panel.select_first_element()
        self.current_panel.is_active = True

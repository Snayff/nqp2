from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    import pygame

    from scripts.core.game import Game
    from scripts.ui_elements.font import Font
    from scripts.ui_elements.unit_stats_frame import UnitStatsFrame


__all__ = ["UI"]


######### TO DO LIST ###############


class UI(ABC):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.default_font: Font = self.game.assets.fonts["default"]
        self.disabled_font: Font = self.game.assets.fonts["disabled"]
        self.warning_font: Font = self.game.assets.fonts["warning"]
        self.positive_font: Font = self.game.assets.fonts["positive"]
        self.instruction_font: Font = self.game.assets.fonts["instruction"]
        self.notification_font: Font = self.game.assets.fonts["notification"]

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
                self.game.assets.get_image("stats", "ration", icon_size),
                str(self.game.memory.rations),
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
        disabled_font = self.disabled_font

        # positions
        start_x = 2
        start_y = 2
        current_x = start_x
        current_y = start_y

        # crate frames
        for key, value in resources.items():
            frame = Frame((current_x, current_y), value[0], (value[1], disabled_font), False)
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
            font = self.warning_font
        else:
            text = self.instruction_text
            font = self.instruction_font

        x = self.game.window.width - font.width(text) - 2
        y = 2
        font.render(text, surface, (x, y))

    def draw_elements(self, surface: pygame.surface):
        for element in self.elements.values():
            element.render(surface)

    def add_panel(self, panel: Panel, name: str):
        """
        Adds panel to the panel dict. If it is the first panel then also sets it to the current panel and selects the
         first element.
        """
        self.panels[name] = panel

        if len(self.panels) == 1:
            self.current_panel = self.panels[name]
            self.current_panel.select_first_element()

    def add_exit_button(self):
        window_width = self.game.window.width
        window_height = self.game.window.height

        confirm_text = "Onwards"
        confirm_width = self.default_font.width(confirm_text)
        current_x = window_width - (confirm_width + GAP_SIZE)
        current_y = window_height - (self.default_font.height + GAP_SIZE)

        frame = Frame((current_x, current_y), text_and_font=(confirm_text, self.default_font), is_selectable=True)
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
        self.current_panel = self.panels[panel_name]
        self.current_panel.select_first_element()
        self.current_panel.is_active = True

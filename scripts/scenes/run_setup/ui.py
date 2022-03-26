from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontEffects, FontType, GAP_SIZE, SceneType
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    from scripts.core.game import Game
    from scripts.scenes.run_setup.scene import RunSetupScene

__all__ = ["RunSetupUI"]


class RunSetupUI(UI):
    """
    Represent the UI of the RunSetupScene.
    """

    def __init__(self, game: Game, parent_scene: RunSetupScene):
        super().__init__(game, True)
        self._parent_scene: RunSetupScene = parent_scene
        self._selected_index: int = 0

        self.set_instruction_text("Choose who will lead the attempt on the throne.")

    def update(self, delta_time: float):
        super().update(delta_time)

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        # panel specific input
        if self._current_panel == self._panels["commanders"]:
            self._handle_select_commander_input()

        # exit panel
        elif self._current_panel == self._panels["exit"]:
            self._handle_exit_input()

    def draw(self, surface: pygame.Surface):

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        commanders = self._game.data.commanders
        selected_commander = self._parent_scene.selected_commander
        window_width = self._game.window.width
        window_height = self._game.window.height
        create_font = self._game.visuals.create_font
        create_fancy_font = self._game.visuals.create_fancy_font
        create_animation = self._game.visuals.create_animation
        get_image = self._game.visuals.get_image

        # positions
        start_x = 0
        start_y = 0

        # draw background
        current_x = start_x
        current_y = start_y
        bg = pygame.Surface((window_width, window_height))
        bg.fill((0, 0, 0))
        frame = Frame(self._game, (current_x, current_y), bg, is_selectable=False)
        self._elements["bg"] = frame

        # draw commanders
        current_x = start_x + 20
        current_y = start_y + 20
        anim_y = current_y + 20
        panel_elements = []
        for selection_counter, commander in enumerate(commanders.values()):
            icon = create_animation(commander["type"], "icon")
            icon.pause()
            frame = Frame(self._game, (current_x, current_y), new_image=icon, is_selectable=False)
            self._elements[f"{commander['type']}_icon"] = frame

            move_anim = create_animation(commander["type"], "move")
            icon.pause()
            icon_width = icon.width
            frame = Frame(self._game, (current_x, anim_y), new_image=move_anim, is_selectable=True)
            self._elements[commander["type"]] = frame

            # highlight selected commander
            if commander["type"] == selected_commander or selected_commander is None:
                frame.is_selected = True
                frame.play_animation()

            panel_elements.append(frame)

            # increment draw pos and counter
            current_x += icon_width + GAP_SIZE

        panel = Panel(self._game, panel_elements, True)
        self.add_panel(panel, "commanders")

        # draw info
        commander = commanders[selected_commander]
        current_y = anim_y + DEFAULT_IMAGE_SIZE + GAP_SIZE
        info_x = start_x + 220
        header_x = start_x + 20

        # name
        frame = Frame(
            self._game, (header_x, current_y), font=create_font(FontType.DISABLED, "Name"), is_selectable=False
        )
        self._elements["name_header"] = frame

        frame = Frame(
            self._game, (info_x, current_y), font=create_font(FontType.DEFAULT, commander["name"]), is_selectable=False
        )
        self._elements["name"] = frame

        current_y += frame.height + GAP_SIZE

        # backstory - N.B. no header and needs wider frame
        line_width = window_width - (current_x * 2)
        max_height = 110
        frame = Frame(
            self._game,
            (header_x, current_y),
            font=create_fancy_font(commander["backstory"], font_effects=[FontEffects.FADE_IN]),
            is_selectable=False,
            max_width=line_width,
            max_height=max_height,
        )
        self._elements["backstory"] = frame

        current_y = (window_height // 2) + 70

        # resources
        frame = Frame(
            self._game, (header_x, current_y), font=create_font(FontType.DISABLED, "Charisma"), is_selectable=False
        )
        self._elements["charisma_header"] = frame

        frame = Frame(
            self._game,
            (info_x, current_y),
            font=create_font(FontType.DEFAULT, commander["charisma"]),
            is_selectable=False,
        )
        self._elements["charisma"] = frame

        current_y += frame.height + GAP_SIZE

        frame = Frame(
            self._game, (header_x, current_y), font=create_font(FontType.DISABLED, "Leadership"), is_selectable=False
        )
        self._elements["leadership_header"] = frame

        frame = Frame(
            self._game,
            (info_x, current_y),
            font=create_font(FontType.DEFAULT, commander["leadership"]),
            is_selectable=False,
        )
        self._elements["leadership"] = frame

        current_y += frame.height + GAP_SIZE

        # gold
        frame = Frame(
            self._game, (header_x, current_y), font=create_font(FontType.DISABLED, "Gold"), is_selectable=False
        )
        self._elements["gold_header"] = frame

        frame = Frame(
            self._game, (info_x, current_y), font=create_font(FontType.DEFAULT, commander["gold"]), is_selectable=False
        )
        self._elements["gold"] = frame

        current_y += frame.height + GAP_SIZE

        # allies
        frame = Frame(
            self._game, (header_x, current_y), font=create_font(FontType.DISABLED, "Allies"), is_selectable=False
        )
        self._elements["allies_header"] = frame

        # draw each faction image
        for count, ally in enumerate(commander["allies"]):
            image = get_image(ally, (DEFAULT_IMAGE_SIZE * 2, DEFAULT_IMAGE_SIZE * 2))
            frame = Frame(self._game, (info_x, current_y), new_image=image, is_selectable=False)
            self._elements[f"allies{count}"] = frame
            info_x += image.width + 2

        # restore selection
        self._current_panel.set_selected_index(self._selected_index)

        self.add_exit_button()

    def _handle_select_commander_input(self):
        is_dirty = False

        # selections within panel
        if self._game.input.states["left"]:

            self._current_panel.select_previous_element()

            # get values to restore after rebuild
            self._parent_scene.selected_commander = list(self._game.data.commanders)[self._current_panel.selected_index]
            self._selected_index = self._current_panel.selected_index

            is_dirty = True

        if self._game.input.states["right"]:

            self._current_panel.select_next_element()

            # get values to restore after rebuild
            self._parent_scene.selected_commander = list(self._game.data.commanders)[self._current_panel.selected_index]
            self._selected_index = self._current_panel.selected_index

            is_dirty = True

        # update selected commander and shown info
        if is_dirty:
            self.rebuild_ui()

        # select option and move to exit
        if self._game.input.states["select"]:
            self._game.input.states["select"] = False

            self.select_panel("exit")

    def _handle_exit_input(self):
        if self._game.input.states["select"]:
            self._game.run_setup.start_run()

        if self._game.input.states["cancel"]:
            # unselect current option
            self._current_panel.unselect_all_elements()

            # change to commanders
            self._current_panel = self._panels["commanders"]

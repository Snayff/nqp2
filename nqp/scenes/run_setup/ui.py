from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.base_classes.image import Image
from nqp.base_classes.ui import UI
from nqp.core.constants import DEFAULT_IMAGE_SIZE, FontEffects, FontType, GAP_SIZE
from nqp.ui_elements.generic.ui_frame import UIFrame
from nqp.ui_elements.generic.ui_panel import UIPanel

if TYPE_CHECKING:
    from nqp.core.game import Game
    from nqp.scenes.run_setup.scene import RunSetupScene

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
        if self._current_container == self._containers["commanders"]:
            self._handle_select_commander_input()

        # exit panel
        elif self._current_container == self._containers["exit"]:
            self._handle_exit_input()

        # info panel
        elif self._current_container == self._containers["info"]:
            self._handle_info_input()

    def draw(self, surface: pygame.Surface):

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def rebuild_ui(self):
        super().rebuild_ui()

        commanders = self._game.data.commanders
        selected_commander = self._parent_scene.selected_commander
        window_width = self._game.window.width
        window_height = self._game.window.height
        create_font = self._game.visual.create_font
        create_fancy_font = self._game.visual.create_fancy_font
        create_animation = self._game.visual.create_animation
        get_image = self._game.visual.get_image

        # positions
        start_x = 0
        start_y = 0

        # draw background
        current_x = start_x
        current_y = start_y
        bg = pygame.Surface((window_width, window_height))
        bg.fill((0, 0, 0))
        bg_image = Image(image=bg)
        frame = UIFrame(self._game, pygame.Vector2(current_x, current_y), image=bg_image, is_selectable=False)
        self._elements["bg"] = frame

        # draw commanders
        current_x = start_x + 20
        current_y = start_y + 20
        anim_y = current_y + 20
        panel_elements = []
        for selection_counter, commander in enumerate(commanders.values()):
            icon = create_animation(commander["type"], "icon")
            icon.pause()
            frame = UIFrame(self._game, pygame.Vector2(current_x, current_y), image=icon, is_selectable=False)
            self._elements[f"{commander['type']}_icon"] = frame

            move_anim = create_animation(commander["type"], "move")
            move_anim.pause()
            icon_width = icon.width
            frame = UIFrame(self._game, pygame.Vector2(current_x, anim_y), image=move_anim, is_selectable=True)
            self._elements[commander["type"]] = frame

            # highlight selected commander
            if commander["type"] == selected_commander or selected_commander is None:
                frame.is_selected = True
                frame.play_animation()

            panel_elements.append(frame)

            # increment draw pos and counter
            current_x += icon_width + GAP_SIZE

        # create panel
        panel = UIPanel(self._game, panel_elements, True)
        self.add_container(panel, "commanders")

        # draw info
        commander = commanders[selected_commander]
        current_y = anim_y + DEFAULT_IMAGE_SIZE + GAP_SIZE
        info_x = start_x + 220
        header_x = start_x + 20

        # name
        frame = UIFrame(
            self._game,
            pygame.Vector2(header_x, current_y),
            font=create_font(FontType.DISABLED, "Name"),
            is_selectable=False,
        )
        self._elements["name_header"] = frame

        frame = UIFrame(
            self._game,
            pygame.Vector2(info_x, current_y),
            font=create_font(FontType.DEFAULT, commander["name"]),
            is_selectable=False,
        )
        self._elements["name"] = frame

        current_y += frame.height + GAP_SIZE

        # backstory - N.B. no header and needs wider frame
        line_width = window_width - (current_x * 2)
        max_height = 110
        frame = UIFrame(
            self._game,
            pygame.Vector2(header_x, current_y),
            font=create_fancy_font(commander["backstory"], font_effects=[FontEffects.FADE_IN]),
            is_selectable=False,
            max_width=line_width,
            max_height=max_height,
        )
        self._elements["backstory"] = frame

        current_y = (window_height // 2) + 70

        # new panel
        panel_elements = []

        # resources
        frame = UIFrame(
            self._game,
            pygame.Vector2(header_x, current_y),
            font=create_font(FontType.DISABLED, "Charisma"),
            is_selectable=False,
        )
        self._elements["charisma_header"] = frame

        frame = UIFrame(
            self._game,
            pygame.Vector2(info_x, current_y),
            font=create_font(FontType.DEFAULT, commander["charisma"]),
            is_selectable=True,
            tooltip_key="charisma"
        )
        self._elements["charisma"] = frame
        panel_elements.append(frame)

        # create panel
        panel = UIPanel(self._game, panel_elements, True)
        self.add_container(panel, "info")

        #
        # current_y += frame.height + GAP_SIZE
        #
        # frame = UIFrame(
        #     self._game,
        #     pygame.Vector2(header_x, current_y),
        #     font=create_font(FontType.DISABLED, "Leadership"),
        #     is_selectable=False,
        # )
        # self._elements["leadership_header"] = frame
        #
        # frame = UIFrame(
        #     self._game,
        #     pygame.Vector2(info_x, current_y),
        #     font=create_font(FontType.DEFAULT, commander["leadership"]),
        #     is_selectable=False,
        # )
        # self._elements["leadership"] = frame
        #
        # current_y += frame.height + GAP_SIZE
        #
        # # gold
        # frame = UIFrame(
        #     self._game,
        #     pygame.Vector2(header_x, current_y),
        #     font=create_font(FontType.DISABLED, "Gold"),
        #     is_selectable=False,
        # )
        # self._elements["gold_header"] = frame
        #
        # frame = UIFrame(
        #     self._game,
        #     pygame.Vector2(info_x, current_y),
        #     font=create_font(FontType.DEFAULT, commander["gold"]),
        #     is_selectable=False,
        # )
        # self._elements["gold"] = frame
        #
        # current_y += frame.height + GAP_SIZE
        #
        # # allies
        # frame = UIFrame(
        #     self._game,
        #     pygame.Vector2(header_x, current_y),
        #     font=create_font(FontType.DISABLED, "Allies"),
        #     is_selectable=False,
        # )
        # self._elements["allies_header"] = frame
        #
        # # draw each faction image
        # for count, ally in enumerate(commander["allies"]):
        #     image = get_image(ally, pygame.Vector2(DEFAULT_IMAGE_SIZE * 2, DEFAULT_IMAGE_SIZE * 2))
        #     frame = UIFrame(self._game, pygame.Vector2(info_x, current_y), image=image, is_selectable=False)
        #     self._elements[f"allies{count}"] = frame
        #     info_x += image.width + 2

        # restore selection in commanders (we want info to reset on commander change)
        if self._current_container == self._containers["commanders"]:
            self._current_container.set_selected_index(self._selected_index)

        self.add_exit_button()

    def _handle_select_commander_input(self):
        is_dirty = False

        # selections within panel
        if self._game.input.states["left"]:

            self._current_container.select_previous_element()

            # get values to restore after rebuild
            self._parent_scene.selected_commander = list(self._game.data.commanders)[
                self._current_container.selected_index
            ]
            self._selected_index = self._current_container.selected_index

            is_dirty = True

        if self._game.input.states["right"]:

            self._current_container.select_next_element()

            # get values to restore after rebuild
            self._parent_scene.selected_commander = list(self._game.data.commanders)[
                self._current_container.selected_index
            ]
            self._selected_index = self._current_container.selected_index

            is_dirty = True

        # update selected commander and shown info
        if is_dirty:
            self.rebuild_ui()

        # select option and move to exit
        if self._game.input.states["select"]:
            self._game.input.states["select"] = False

            self.select_container("exit")

        if self._game.input.states["ctrl"]:
            self.select_container("info")

    def _handle_exit_input(self):
        if self._game.input.states["select"]:
            self._game.run_setup.start_run()

        if self._game.input.states["cancel"]:
            # unselect current option
            self._current_container.unselect_all_elements()

            # change to commanders
            self._current_container = self._containers["commanders"]

    def _handle_info_input(self):
        if self._game.input.states["ctrl"]:
            self.select_container("commanders")

            # selections within panel
            if self._game.input.states["up"]:
                self._current_container.select_previous_element()

            if self._game.input.states["down"]:
                self._current_container.select_next_element()

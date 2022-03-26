from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from scripts.core import utility
from scripts.core.base_classes.ui import UI
from scripts.core.constants import (
    ChooseRoomState,
    CombatState,
    DEFAULT_IMAGE_SIZE,
    EventState,
    FontEffects,
    FontType,
    GAP_SIZE,
    InnState,
    SceneType,
    TILE_SIZE,
    TrainingState,
    WorldState,
)
from scripts.scene_elements.unitgrid import UnitGrid
from scripts.scene_elements.world_view import WorldView
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Optional

    from scripts.core.game import Game
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

        self.grid: Optional[UnitGrid] = None

    def draw(self, surface: pygame.Surface):
        state = self._parent_scene.model.state

        self._worldview.draw(surface)
        offset = self._worldview.camera.render_offset()

        # TODO: create and move to mouse tool system
        if state == WorldState.CHOOSE_NEXT_ROOM:
            if self.grid:
                self.grid.draw(surface, offset)

        self._draw_instruction(surface)
        self._draw_elements(surface)

    def update(self, delta_time: float):
        super().update(delta_time)

        self._worldview.update(delta_time)

        state = self._parent_scene.model.state
        if state == WorldState.CHOOSE_NEXT_ROOM:
            self._update_choose_room(delta_time)
        elif state == WorldState.COMBAT:
            self._update_combat(delta_time)
        elif state == WorldState.TRAINING:
            self._update_training(delta_time)

    def _update_choose_room(self, delta_time: float):
        # need to call here as otherwise units dont align to grid
        # TODO - remove the need to call after init
        if self.grid is None:
            self.grid = UnitGrid(self._game, pygame.Rect(3, 2, 3, 6))
            self.grid.move_units_to_grid()

    def _update_combat(self, delta_time: float):
        controller = self._parent_scene.combat
        local_state = controller.state

        if local_state == CombatState.VICTORY:
            self._parent_scene.combat.victory_duration += delta_time
            if self._parent_scene.combat.victory_duration >= 3:
                self.rebuild_ui()

    def _update_training(self, delta_time: float):
        pass

    def process_input(self, delta_time: float):
        super().process_input(delta_time)

        state = self._parent_scene.model.state

        if state == WorldState.CHOOSE_NEXT_ROOM:
            self._process_choose_next_room_input()

            if self._parent_scene.choose_room.state == ChooseRoomState.IDLE:
                if self.grid:
                    self.grid.process_input()

        elif state == WorldState.COMBAT:
            self._process_combat_input()
        elif state == WorldState.TRAINING:
            self._process_training_input()
        elif state == WorldState.INN:
            self._process_inn_input()
        elif state == WorldState.EVENT:
            self._process_event_input()

        #################
        # DO NOT DELETE #
        #################
        # TODO - add flag and add trigger to dev console
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

    def _process_inn_input(self):
        controller = self._parent_scene.inn
        local_state = controller.state
        is_ui_dirty = False

        if local_state == InnState.IDLE:
            # toggle select upgrade or view units
            if self._game.input.states["shift"]:
                controller.state = InnState.CHOOSE_UNIT
                self._current_panel.set_selectable(True)
                is_ui_dirty = True

            # move to choose room
            if self._game.input.states["cancel"]:
                self._parent_scene.model.state = WorldState.CHOOSE_NEXT_ROOM
                controller.delete_troupe()
                is_ui_dirty = True

        if local_state == InnState.CHOOSE_UNIT:
            # frame selection
            if self._game.input.states["up"]:
                self._current_panel.select_previous_element()

                # update selected unit
                current_index = self._current_panel.selected_index
                controller.selected_unit = controller.units_available[current_index]

                self._refresh_info_pane()

            if self._game.input.states["down"]:
                self._current_panel.select_next_element()

                # update selected unit
                current_index = self._current_panel.selected_index
                controller.selected_unit = controller.units_available[current_index]

                self._refresh_info_pane()

            # select unit
            if self._game.input.states["select"]:

                # handle purchase
                controller.recruit_unit(controller.selected_unit)
                self.grid.move_units_to_grid()

                # revert to previous state
                controller.state = InnState.IDLE
                self._current_panel.set_selectable(False)
                is_ui_dirty = True
                controller.selected_unit = None

                # confirm
                self.set_instruction_text("Unit recruited.", True)

            # toggle view units
            if self._game.input.states["shift"]:
                controller.state = TrainingState.IDLE
                self._current_panel.set_selectable(False)

        if is_ui_dirty:
            self.rebuild_ui()

    def _process_combat_input(self):
        controller = self._parent_scene.combat
        local_state = controller.state

        if local_state == CombatState.IDLE:
            if self._game.input.states["shift"]:
                self._parent_scene.combat.prepare_combat()

        elif local_state == CombatState.DEFEAT:
            if self._game.input.states["select"]:
                self._game.memory.reset()
                self._game.change_scene(SceneType.MAIN_MENU)

        elif local_state == CombatState.VICTORY:
            if self._game.input.states["select"]:
                self._parent_scene.model.state = WorldState.CHOOSE_NEXT_ROOM

    def _process_training_input(self):
        controller = self._parent_scene.training
        local_state = controller.state
        is_ui_dirty = False

        if local_state == TrainingState.IDLE:
            # toggle to select upgrade
            if self._game.input.states["shift"]:
                controller.state = TrainingState.CHOOSE_UPGRADE
                self._current_panel.set_selectable(True)
                is_ui_dirty = True

            # move to choose room
            if self._game.input.states["cancel"]:
                self._parent_scene.model.state = WorldState.CHOOSE_NEXT_ROOM
                is_ui_dirty = True

        if local_state == TrainingState.CHOOSE_UPGRADE:
            # frame selection
            if self._game.input.states["up"]:
                self._current_panel.select_previous_element()
                self._refresh_info_pane()

            if self._game.input.states["down"]:
                self._current_panel.select_next_element()
                self._refresh_info_pane()

            # select upgrade
            if self._game.input.states["select"]:
                controller.state = TrainingState.CHOOSE_TARGET_UNIT
                controller.current_grid_index = 0
                self._current_panel.set_selectable(False)
                is_ui_dirty = True

            # toggle to view units
            if self._game.input.states["shift"]:
                controller.state = TrainingState.IDLE
                self._current_panel.set_selectable(False)

        if local_state == TrainingState.CHOOSE_TARGET_UNIT:
            # cancel
            if self._game.input.states["cancel"]:
                controller.state = TrainingState.CHOOSE_UPGRADE
                self.grid.units[controller.current_grid_index].is_selected = False
                self._current_panel.set_selectable(True)
                is_ui_dirty = True

            # unit selection
            # TODO - update to allow moving around the grid rather than jumping indices
            current_index = controller.current_grid_index
            new_index = current_index
            if self._game.input.states["up"]:
                self.grid.units[current_index].is_selected = False
                new_index = utility.next_number_in_loop(current_index, len(self.grid.units))
            elif self._game.input.states["down"]:
                self.grid.units[current_index].is_selected = False
                new_index = utility.previous_number_in_loop(current_index, len(self.grid.units))

            controller.current_grid_index = new_index
            self.grid.units[new_index].is_selected = True

            # apply upgrade
            if self._game.input.states["select"]:
                controller.upgrade_unit(self.grid.units[current_index])

                # confirm
                self.set_instruction_text("Unit upgraded.", True)

                # revert to previous state
                self.grid.units[current_index].is_selected = False
                controller.state = TrainingState.CHOOSE_UPGRADE
                self._current_panel.set_selectable(True)

                is_ui_dirty = True

        if is_ui_dirty:
            self.rebuild_ui()

    def _process_choose_next_room_input(self):
        controller = self._parent_scene.choose_room
        local_state = controller.state
        is_ui_dirty = False

        if local_state == ChooseRoomState.IDLE:
            # move to select room
            if self._game.input.states["shift"]:
                controller.state = ChooseRoomState.CHOOSE_ROOM
                self._current_panel.set_selectable(True)

        if local_state == ChooseRoomState.CHOOSE_ROOM:
            # frame selection
            current_index = controller.current_index
            new_index = current_index
            if self._game.input.states["up"]:
                self._current_panel.select_previous_element()
                new_index = utility.previous_number_in_loop(current_index, len(controller.choices))

            if self._game.input.states["down"]:
                self._current_panel.select_next_element()
                new_index = utility.next_number_in_loop(current_index, len(controller.choices))

            # set new index to track selection
            controller.current_index = new_index

            # select upgrade
            if self._game.input.states["select"]:
                controller.selected_room = controller.choices[controller.current_index][0]
                controller.begin_move_to_new_room()
                self.set_instruction_text("")
                is_ui_dirty = True

            # toggle back to idle
            if self._game.input.states["shift"]:
                controller.state = ChooseRoomState.IDLE
                self.grid.move_units_to_grid()
                self._current_panel.set_selectable(False)

        if is_ui_dirty:
            self.rebuild_ui()

    def _process_event_input(self):
        controller = self._parent_scene.event
        local_state = controller.state
        current_index = controller.current_index
        is_ui_dirty = False

        if local_state == EventState.IDLE:
            # frame selection
            new_index = current_index
            if self._game.input.states["up"]:
                self._current_panel.select_previous_element()
                new_index = utility.previous_number_in_loop(current_index, len(controller.active_event["options"]))

            if self._game.input.states["down"]:
                self._current_panel.select_next_element()
                new_index = utility.next_number_in_loop(current_index, len(controller.active_event["options"]))

            # set new index to track selection
            controller.current_index = new_index

            # select option
            if self._game.input.states["select"]:
                self._parent_scene.event.trigger_result()
                controller.state = EventState.SHOW_RESULT
                is_ui_dirty = True

        if local_state == EventState.SHOW_RESULT:

            # complete move to next room
            if self._game.input.states["select"]:
                # check there is a next state
                if self._parent_scene.model.next_state is not None:
                    self._parent_scene.model.go_to_next_state()
                    is_ui_dirty = True
                else:
                    raise Exception(f"_process_event_input: Tried to move to next state, but there isnt one.")

        if is_ui_dirty:
            self.rebuild_ui()

    def rebuild_ui(self):
        super().rebuild_ui()

        state = self._parent_scene.model.state

        if state == WorldState.CHOOSE_NEXT_ROOM:
            self._rebuild_choose_next_room_ui()
        elif state == WorldState.COMBAT:
            self._rebuild_combat_ui()
        elif state == WorldState.TRAINING:
            self._rebuild_training_ui()
        elif state == WorldState.INN:
            self._rebuild_inn_ui()
        elif state == WorldState.EVENT:
            self._rebuild_event_ui()

    def _rebuild_choose_next_room_ui(self):
        create_font = self._game.visuals.create_font
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x = self._game.window.width - 100
        start_y = 100
        controller = self._parent_scene.choose_room

        # draw room choices
        current_x = start_x
        current_y = start_y
        panel_list = []
        for i, room_and_if_hidden in enumerate(controller.choices):
            room_type, is_hidden = room_and_if_hidden

            # get icon
            if is_hidden:
                icon = self._game.visuals.get_image("unknown_room", icon_size)
                text = "Unknown"
            else:
                icon = self._game.visuals.get_image(room_type, icon_size)
                text = room_type
            frame = Frame(
                (current_x, current_y),
                new_image=icon,
                font=create_font(FontType.DEFAULT, text),
            )

            # register elements
            self._elements[f"{room_type}_{i}"] = frame
            panel_list.append(frame)

            current_y += 100

        # build panel
        panel = Panel(panel_list, True)
        self.add_panel(panel, "room_choices")

        # handle instructions  for different states
        if controller.state == ChooseRoomState.CHOOSE_ROOM:
            self.set_instruction_text("Press X to cancel.")

            # ensure an room is selected
            if controller.selected_room is None:
                controller.selected_room = controller.choices[0][0]

        elif controller.state == ChooseRoomState.IDLE:
            self.set_instruction_text("Press shift to select a room.")

    def _rebuild_training_ui(self):
        create_font = self._game.visuals.create_font
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x = self._game.window.centre[0]
        start_y = 100
        controller = self._parent_scene.training
        model = self._parent_scene.model

        # draw upgrades
        current_x = start_x
        current_y = start_y
        panel_list = []
        for i, upgrade in enumerate(controller.upgrades_available):
            # check if available
            if upgrade is not None:
                text = f"{upgrade['stat']} +{upgrade['mod_amount']}"
                font_type = FontType.DEFAULT
                is_selectable = True

                # check can afford
                upgrade_cost = controller.calculate_upgrade_cost(upgrade["tier"])
                can_afford = model.gold > upgrade_cost
                if can_afford:
                    gold_font_type = FontType.DEFAULT
                else:
                    gold_font_type = FontType.NEGATIVE

                # draw gold cost
                gold_icon = self._game.visuals.get_image("gold", icon_size)
                frame = Frame(
                    (current_x + 100, current_y),
                    new_image=gold_icon,
                    font=create_font(gold_font_type, str(upgrade_cost)),
                    is_selectable=False,
                )
                self._elements["cost" + str(i)] = frame

                upgrade_icon = self._game.visuals.get_image(upgrade["type"], icon_size)

            else:
                text = f"Sold out"
                font_type = FontType.DISABLED
                is_selectable = False

                upgrade_icon = None

            # draw upgrade icon and details
            frame = Frame(
                (current_x, current_y),
                new_image=upgrade_icon,
                font=create_font(font_type, text),
                is_selectable=is_selectable,
            )
            # capture frame
            self._elements[upgrade["type"]] = frame
            panel_list.append(frame)

            # increment
            current_y += icon_height + GAP_SIZE

        panel = Panel(panel_list, True)
        self.add_panel(panel, "upgrades")

        # handle instructions and selectability for different states
        if controller.state == TrainingState.CHOOSE_UPGRADE:
            panel.set_selectable(True)
            self.set_instruction_text("Press shift to go back to the troupe.")

            # ensure an upgrade is selected
            if controller.selected_upgrade is None:
                controller.selected_upgrade = controller.upgrades_available[0].copy()

            self._refresh_info_pane()

        elif controller.state == TrainingState.IDLE:
            self.set_instruction_text("Press shift to select upgrades or X to go to choose the next room.")

        elif controller.state == TrainingState.CHOOSE_TARGET_UNIT:
            self.set_instruction_text("Press enter to apply the upgrade or X to cancel.")

    def _refresh_info_pane(self):
        """
        Refresh the info pane's info
        """
        # TODO - fix info pane not refreshing to match selection
        create_font = self._game.visuals.create_font

        if self._parent_scene.model.state == WorldState.TRAINING:
            controller = self._parent_scene.training
            upgrade = controller.selected_upgrade
            highlighted_frame = self._elements[controller.selected_upgrade["type"]]
            desc = upgrade["desc"]

        elif self._parent_scene.model.state == WorldState.INN:
            controller = self._parent_scene.inn

            if controller.selected_unit is not None:
                unit_index = controller.units_available.index(controller.selected_unit)
                highlighted_frame = self._elements[f"banner{unit_index}"]
                desc = controller.selected_unit.type
            else:
                highlighted_frame = list(self._elements.values())[0]
                desc = ""

        else:
            return

        info_x = highlighted_frame.x + highlighted_frame.width + 20
        font_type = FontType.DEFAULT

        frame = Frame((info_x, highlighted_frame.y), font=create_font(font_type, desc))
        self._elements["info_pane"] = frame

    def _rebuild_combat_ui(self):
        controller = self._parent_scene.combat
        local_state = controller.state
        create_font = self._game.visuals.create_font
        start_x, start_y = self._game.window.centre

        # draw upgrades
        current_x = start_x
        current_y = start_y

        if local_state == CombatState.IDLE:
            self.set_instruction_text("Press shift to start combat.")

        elif local_state == CombatState.VICTORY:
            frame = Frame(
                (current_x, current_y),
                font=create_font(FontType.POSITIVE, "Victory"),
                is_selectable=False,
            )
            self._elements["victory_notification"] = frame

            self.set_instruction_text("Press Enter to continue.")
            self.add_exit_button()
            self.select_panel("exit")

        elif local_state == CombatState.DEFEAT:

            icon_width = DEFAULT_IMAGE_SIZE
            icon_height = DEFAULT_IMAGE_SIZE
            icon_size = (icon_width, icon_height)

            # draw upgrades
            current_x = start_x
            current_y = start_y
            defeat_icon = self._game.visuals.get_image("arrow_button", icon_size)
            frame = Frame(
                (current_x, current_y),
                new_image=defeat_icon,
                font=create_font(FontType.NEGATIVE, "Defeated"),
                is_selectable=False,
            )
            self._elements["defeat_notification"] = frame

            current_y += 100

            frame = Frame(
                (current_x, current_y),
                new_image=defeat_icon,
                font=create_font(FontType.DEFAULT, "Press Enter to return to the main menu."),
                is_selectable=False,
            )
            self._elements["defeat_instruction"] = frame

            self.set_instruction_text("Press Enter to return to main menu.")
            self.add_exit_button()
            self.select_panel("exit")

    def _rebuild_inn_ui(self):
        create_font = self._game.visuals.create_font
        icon_width = DEFAULT_IMAGE_SIZE
        icon_height = DEFAULT_IMAGE_SIZE
        icon_size = (icon_width, icon_height)
        start_x = self._game.window.centre[0]
        start_y = 100
        y_increment = 100
        controller = self._parent_scene.inn
        model = self._parent_scene.model
        panel_list = []

        # draw unit positions
        for i in range(controller.num_units):
            current_x = start_x
            current_y = start_y + (i * y_increment)

            # check available
            if controller.units_available[i] is None:
                continue

            # check can recruit
            upgrade_cost = controller.units_available[i].gold_cost
            can_afford = model.gold > upgrade_cost
            has_space = model.charisma_remaining > 0
            if can_afford and has_space:
                gold_font_type = FontType.DEFAULT
                can_buy = True
            else:
                gold_font_type = FontType.NEGATIVE
                can_buy = False

            # draw gold cost
            gold_icon = self._game.visuals.get_image("gold", icon_size)
            frame = Frame(
                (current_x + 20, current_y),
                new_image=gold_icon,
                font=create_font(gold_font_type, str(upgrade_cost)),
                is_selectable=False,
            )
            self._elements["cost" + str(i)] = frame

            # draw banner in frame, to allow selection
            banner = self._game.visuals.get_image("banner", icon_size)
            frame = Frame(
                (current_x, current_y),
                new_image=banner,
                is_selectable=can_buy,
            )
            self._elements["banner" + str(i)] = frame
            panel_list.append(frame)

            # update unit pos
            unit = controller.units_available[i]
            unit.set_position([current_x, current_y])

        panel = Panel(panel_list, True)
        self.add_panel(panel, "units")

        # handle instructions and selectability for different states
        if controller.state == InnState.CHOOSE_UNIT:
            panel.set_selectable(True)
            self.set_instruction_text("Press shift to go back to the troupe.")

            # ensure an upgrade is selected
            if controller.selected_unit is None:
                controller.selected_unit = controller.units_available[0]

            self._refresh_info_pane()

        elif controller.state == InnState.IDLE:
            self.set_instruction_text("Press shift to select Units or X to choose the next room.")

    def _rebuild_event_ui(self):
        create_font = self._game.visuals.create_font
        create_fancy_font = self._game.visuals.create_fancy_font
        window_width = self._game.window.width
        window_height = self._game.window.height
        start_x = 50
        start_y = 20
        frame_line_width = window_width - (start_x * 2)
        event = self._parent_scene.event.active_event
        show_event_result = self._game.data.options["show_event_option_result"]
        state = self._parent_scene.event.state
        controller = self._parent_scene.event
        panel_list = []

        # draw background
        bg_width = window_width - (start_x * 2)
        bg_height = window_height - (start_y * 2)
        bg = pygame.Surface((bg_width, bg_height), SRCALPHA)
        bg.fill((0, 0, 0, 150))
        frame = Frame((start_x, start_y), image=bg)
        self._elements[f"background"] = frame

        # get image info inc. ratio to scale properly
        image = self._game.visuals.get_image(event["image"])
        image_size_ratio = image.width // image.height
        image_width = DEFAULT_IMAGE_SIZE * 6
        image_height = image_width * image_size_ratio

        # draw image
        current_x = start_x
        current_y = start_y + (image_height // 2)
        image = self._game.visuals.get_image(event["image"], (image_width, image_height))
        frame = Frame(
            (current_x, current_y),
            new_image=image,
            is_selectable=False,
        )
        self._elements["image"] = frame

        # draw description
        current_x += image_width + 5
        current_y = start_y
        if controller.state == EventState.IDLE:
            fancy_font = create_fancy_font(event["description"], font_effects=[FontEffects.FADE_IN])
        else:
            fancy_font = create_fancy_font(event["description"])
        font_height = fancy_font.line_height
        max_height = ((window_height // 2) - current_y) - font_height
        desc_width = frame_line_width - image_width
        frame = Frame(
            (current_x, current_y),
            font=fancy_font,
            max_height=max_height,
            max_width=desc_width,
            is_selectable=False,
        )
        self._elements["description"] = frame

        # move to half way down screen
        current_y = window_height // 2

        # draw separator
        offset = 80
        line_width = window_width - (offset * 2)
        surface = pygame.Surface((line_width, 1))
        pygame.draw.line(surface, (117, 50, 168), (0, 0), (line_width, 0))
        frame = Frame((offset, current_y), surface)
        self._elements["separator"] = frame

        # draw event contents; either options or results
        if state == EventState.IDLE:

            for counter, option in enumerate(event["options"]):
                # get option text
                if show_event_result:
                    option_text = option["text"] + " [" + option["displayed_result"] + "]"
                else:
                    option_text = option["text"]

                # build frame
                frame = Frame(
                    (current_x, current_y), font=create_font(FontType.DEFAULT, option_text), is_selectable=True
                )
                self._elements[f"option_{counter}"] = frame
                panel_list.append(frame)

                # increment position
                current_y += frame.height + GAP_SIZE

            # create panel
            panel = Panel(panel_list, True)
            self.add_panel(panel, "options")

        # show results
        elif state == EventState.SHOW_RESULT:
            # indent x
            current_x = window_width // 4

            # draw option chosen
            selected_option = controller.active_event["options"][controller.current_index]["text"]
            frame = Frame(
                (current_x, current_y), font=create_font(FontType.DEFAULT, selected_option), is_selectable=True
            )
            self._elements["selected_option"] = frame

            # increment position
            current_y += frame.height + (GAP_SIZE * 2)

            # centre results
            current_x = (window_width // 2) - (DEFAULT_IMAGE_SIZE // 2)

            # draw results
            results = controller.active_event["options"][controller.current_index]["result"]
            for counter, result in enumerate(results):
                key, value, target = self._parent_scene.event.parse_event_string(result)

                # only show results we want the player to be aware of
                if key in ["unlock_event"]:
                    continue

                # get image
                result_image = controller.get_result_image(key, value, target)

                # get font
                try:
                    if int(value) > 0:
                        # more injuries is bad, unlike other resources
                        if key not in ["injury"]:
                            font_type = FontType.POSITIVE
                        else:
                            font_type = FontType.NEGATIVE
                    else:
                        # less injuries is good, unlike other resources
                        if key in ["injury"]:
                            font_type = FontType.POSITIVE
                        else:
                            font_type = FontType.NEGATIVE

                    # we know its a number, so take as value
                    text = value
                except ValueError:
                    # string could not be converted to int
                    font_type = FontType.POSITIVE

                    # generic message to handle adding units
                    text = "recruited."

                # create the frame
                frame = Frame(
                    (current_x, current_y),
                    new_image=result_image,
                    font=create_font(font_type, text),
                    is_selectable=False,
                )
                self._elements[f"result_{counter}"] = frame
                panel_list.append(frame)

                # increment position
                current_y += frame.height + GAP_SIZE

            # only draw exit button once decision made
            self.add_exit_button()
            self.select_panel("exit")

            # create panel
            panel = Panel(panel_list, True)
            panel.set_selectable(False)
            self.add_panel(panel, "results")

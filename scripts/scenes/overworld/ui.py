from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

import pygame

from scripts.core import utility
from scripts.core.base_classes.ui import UI
from scripts.core.constants import NodeType, OverworldState, SceneType

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["OverworldUI"]


############# TO DO LIST ##################

class OverworldUI(UI):
    """
    Represents the overworld UI.
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.selected_node = 0  # node index

        self.set_instruction_text("Choose where you will go next.")

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.game.overworld.state == OverworldState.READY:
            #row_nodes = self.game.overworld.nodes[self.game.overworld.current_node_row]

            if self.game.input.states["left"]:
                self.game.input.states["left"] = False
                self.selected_node -= 1
                if self.selected_node < 0:
                    self.selected_node = len(row_nodes) - 1

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False
                self.selected_node += 1
                if self.selected_node >= len(row_nodes):
                    self.selected_node = 0

            if self.game.input.states["select"]:
                self.game.input.states["select"] = False

                selected_node = self.game.overworld.nodes[self.game.overworld.current_node_row][self.selected_node]
                selected_node_type = selected_node.type

                logging.info(f"Next node, {selected_node_type.name}, selected.")

                # change active scene
                if selected_node_type == NodeType.COMBAT:
                    scene = SceneType.COMBAT
                elif selected_node_type == NodeType.INN:
                    scene = SceneType.INN
                elif selected_node_type == NodeType.TRAINING:
                    scene = SceneType.TRAINING
                elif selected_node_type == NodeType.EVENT:
                    scene = SceneType.EVENT
                else:
                    # selected_node_type == NodeType.UNKNOWN:
                    node_type = self.game.overworld.get_random_node_type(False)
                    scene = utility.node_type_to_scene_type(node_type)

                self.game.change_scene(scene)

                self.game.overworld.increment_row()

            if self.game.input.states["view_troupe"]:
                self.game.input.states["view_troupe"] = False
                self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.surface):
        overworld_map = self.game.overworld

        if overworld_map.state == OverworldState.LOADING:
            # draw loading screen
            window_height = self.game.window.height
            self.game.assets.fonts["warning"].render("Loading...", surface, (10, window_height - 20))

        elif overworld_map.state == OverworldState.READY:
            # # get node icon details
            # node_width = overworld_map.nodes[0][0].icon.get_width()
            # node_height = overworld_map.nodes[0][0].icon.get_height()
            # line_offset = 2
            #
            # # draw node connections
            # for row in overworld_map.nodes:
            #     for node in row:
            #         for connected_node in node.connected_previous_row_nodes:
            #             # get positions
            #             node_centre_x = node.pos[0] + (node_width / 2)
            #             node_top = node.pos[1] - line_offset
            #             connected_node_centre = connected_node.pos[0] + (node_width / 2)
            #             connected_node_bottom = connected_node.pos[1] + node_height + line_offset
            #             # FIXME - are these nodes the wrong way round?
            #
            #             pygame.draw.line(
            #                 surface,
            #                 (255, 255, 255),
            #                 (node_centre_x, node_top),
            #                 (connected_node_centre, connected_node_bottom),
            #             )
            #
            # # draw selection
            # selected_node = overworld_map.nodes[overworld_map.current_node_row][self.selected_node]
            # selected_node_centre_x = selected_node.pos[0] + (node_width / 2)
            # selected_node_centre_y = selected_node.pos[1] + (node_height / 2)
            # pygame.draw.circle(surface, (255, 0, 0), (selected_node_centre_x, selected_node_centre_y), node_width, 2)

            self.draw_instruction(surface)

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.misc.constants import MapState, NodeType

if TYPE_CHECKING:
    from scripts.management.game import Game


__all__ = ["OverworldUI"]


class OverworldUI:
    """
    Represents the overworld UI.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.selected_node = 0  # node index

    def update(self):

        if self.game.overworld.map.state == MapState.READY:
            row_nodes = self.game.overworld.map.nodes[self.game.overworld.map.active_row]

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

                selected_node = self.game.overworld.map.nodes[self.game.overworld.map.active_row][self.selected_node]
                selected_node_type = selected_node.type

                # change active screen
                if selected_node_type == NodeType.COMBAT:
                    self.game.active_screen = self.game.combat
                elif selected_node_type == NodeType.INN:
                    # TODO - update to inn
                    self.game.active_screen = self.game.combat
                elif selected_node_type == NodeType.TRAINING:
                    # TODO - update to training
                    self.game.active_screen = self.game.combat
                elif selected_node_type == NodeType.EVENT:
                    self.game.active_screen = self.game.event

                self.game.overworld.map.active_row += 1

    def render(self, surface: pygame.surface):
        overworld_map = self.game.overworld.map

        if overworld_map.state == MapState.LOADING:
            # draw loading screen
            window_height = self.game.window.height
            self.game.assets.fonts["small_red"].render("Loading...", surface, (10, window_height - 20))

        elif overworld_map.state == MapState.READY:
            # get node icon details
            node_width = overworld_map.nodes[0][0].icon.get_width()
            node_height = overworld_map.nodes[0][0].icon.get_height()
            line_offset = 2

            # draw node connections
            for row in overworld_map.nodes:
                for node in row:
                    for connected_node in node.connected_previous_row_nodes:
                        # get positions
                        node_centre_x = node.pos[0] + (node_width / 2)
                        node_top = node.pos[1] - line_offset
                        connected_node_centre = connected_node.pos[0] + (node_width / 2)
                        connected_node_bottom = connected_node.pos[1] + node_height + line_offset
                        # FIXME - are these nodes the wrong way round?

                        pygame.draw.line(
                            surface,
                            (255, 255, 255),
                            (node_centre_x, node_top),
                            (connected_node_centre, connected_node_bottom),
                        )

            # draw selection
            selected_node = overworld_map.nodes[overworld_map.active_row][self.selected_node]
            selected_node_centre_x = selected_node.pos[0] + (node_width / 2)
            selected_node_centre_y = selected_node.pos[1] + (node_height / 2)
            pygame.draw.circle(surface, (255, 0, 0), (selected_node_centre_x, selected_node_centre_y), node_width, 2)

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.misc.constants import MapState

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

                # TODO - Trigger the node, e.g. the event,  combat etc. - change the active screen

                self.game.overworld.map.active_row += 1

    def render(self, surface: pygame.surface):
        if self.game.overworld.map.state == MapState.LOADING:
            window_height = self.game.window.base_resolution[1]
            self.game.assets.fonts["small_red"].render("Loading...", surface, (10, window_height - 20))

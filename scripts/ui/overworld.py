from __future__ import annotations

from typing import TYPE_CHECKING
import pygame

from scripts.misc.constants import DEFAULT_IMAGE_SIZE, NodeType

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
        row_nodes = self.game.overworld.map.nodes[self.game.overworld.map.current_row]
        
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

            # TODO - Trigger the node, e.g. the event,  combat etc.

            self.game.overworld.map.current_row += 1

        
    def render(self, surface: pygame.surface):
        pass




    
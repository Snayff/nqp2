from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

import pygame

from scripts.core import utility
from scripts.core.base_classes.ui import UI
from scripts.core.constants import Direction, NodeType, OverworldState, SceneType

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

        self.set_instruction_text("Choose where you will go next.")

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.game.overworld.state == OverworldState.READY:

            node_container = self.game.overworld.node_container

            if self.game.input.states["left"]:
                self.game.input.states["left"] = False
                node_container.select_next_node(Direction.LEFT)

            if self.game.input.states["right"]:
                self.game.input.states["right"] = False
                node_container.select_next_node(Direction.RIGHT)

            if self.game.input.states["up"]:
                self.game.input.states["up"] = False
                node_container.select_next_node(Direction.UP)

            if self.game.input.states["down"]:
                self.game.input.states["down"] = False
                node_container.select_next_node(Direction.DOWN)

            # if self.game.input.states["select"]:
            #     self.game.input.states["select"] = False
            #
            #     selected_node = self.game.overworld.nodes[self.game.overworld.current_node_row][self.selected_node]
            #     selected_node_type = selected_node.type
            #
            #     logging.info(f"Next node, {selected_node_type.name}, selected.")
            #
            #     # change active scene
            #     if selected_node_type == NodeType.COMBAT:
            #         scene = SceneType.COMBAT
            #     elif selected_node_type == NodeType.INN:
            #         scene = SceneType.INN
            #     elif selected_node_type == NodeType.TRAINING:
            #         scene = SceneType.TRAINING
            #     elif selected_node_type == NodeType.EVENT:
            #         scene = SceneType.EVENT
            #     else:
            #         # selected_node_type == NodeType.UNKNOWN:
            #         node_type = self.game.overworld.get_random_node_type(False)
            #         scene = utility.node_type_to_scene_type(node_type)
            #
            #     self.game.change_scene(scene)
            #
            #     self.game.overworld.increment_row()

            if self.game.input.states["view_troupe"]:
                self.game.input.states["view_troupe"] = False
                self.game.change_scene(SceneType.VIEW_TROUPE)

    def render(self, surface: pygame.surface):
        overworld_map = self.game.overworld

        if overworld_map.state == OverworldState.LOADING:
            # draw loading screen
            window_height = self.game.window.height
            self.warning_font.render("Loading...", surface, (10, window_height - 20))

        elif overworld_map.state == OverworldState.READY:
            self.draw_instruction(surface)

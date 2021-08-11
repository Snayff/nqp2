from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import pygame
import pytweening

from scripts.core import utility
from scripts.core.constants import Direction, NodeType, OverworldState, SceneType

from abc import ABC, abstractmethod

from scripts.scenes.overworld.elements.node2 import Node2

if TYPE_CHECKING:
    from scripts.core.game import Game
    from typing import List, Tuple, Dict, Optional

__all__ = ["NodeContainer"]


class NodeContainer(ABC):
    def __init__(self, game: Game):
        self.game: Game = game

        self.selected_node: Optional[Node2] = None
        self.target_node: Optional[Node2] = None
        self.selection_pos: Tuple[float, float] = (0, 0)  # where the selection is drawn

        self.max_travel_time: float = 0.5
        self.current_travel_time: float = 0.0
        self.is_travel_paused: bool = False
        self.is_due_event: bool = False  # true if waiting for an event to trigger
        self.events_triggered: int = 0  # number of events triggered so far

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass

    @abstractmethod
    def update(self, delta_time: float):
        pass

    @abstractmethod
    def select_next_node(self, direction: Direction):
        pass

    @abstractmethod
    def generate_nodes(self):
        pass

    def roll_for_event(self):
        """
        Roll to see if an event will be triggered when transitioning between nodes.
        """
        # check if we have hit the limit of events
        if self.events_triggered >= self.game.data.config["overworld"]["max_events_per_level"]:
            return

        if self.game.rng.roll() < self.game.data.config["overworld"]["chance_of_event"]:
            self.is_due_event = True

    def _get_node_icon(self, node_type: NodeType) -> pygame.Surface:
        """
        Get the node icon from the node type
        """
        if node_type == NodeType.COMBAT:
            node_icon = self.game.assets.get_image("nodes", "combat")
        elif node_type == NodeType.EVENT:
            node_icon = self.game.assets.get_image("nodes", "event")
        elif node_type == NodeType.INN:
            node_icon = self.game.assets.get_image("nodes", "inn")
        elif node_type == NodeType.TRAINING:
            node_icon = self.game.assets.get_image("nodes", "training")
        else:
            # node_type == NodeType.UNKNOWN
            node_icon = self.game.assets.get_image("nodes", "unknown")

        return node_icon

    def _get_random_node_type(self, allow_unknown: bool = True) -> NodeType:
        """
        Return a random node type
        """
        node_weights_dict = self.game.data.config["overworld"]["node_weights"]
        node_types = [NodeType.COMBAT, NodeType.INN, NodeType.TRAINING]

        if allow_unknown:
            node_types.append(NodeType.UNKNOWN)

        node_weights = []
        try:
            for enum_ in node_types:
                name = enum_.name.lower()
                node_weights.append(node_weights_dict[name])

        except KeyError as key_error:
            logging.warning(f"generate_map: Node key not found in config file. Defaults used. err:{key_error}")

            # overwrite with default
            node_weights = []
            for enum_ in node_types:
                node_weights.append(0.1)

        node_type = self.game.rng.choices(node_types, node_weights, k=1)[0]

        return node_type

    def _transition_to_new_node(self, delta_time: float):
        """
        Move the selection pos from the selected node to the target node. Update selected node when complete.
        """
        target = self.target_node
        selected = self.selected_node

        # update timer
        self.current_travel_time += delta_time
        percent_time_complete = min(1.0, self.current_travel_time / self.max_travel_time)

        # update selection position
        lerp_amount = pytweening.easeInQuad(percent_time_complete)
        x = utility.lerp(selected.pos[0], target.pos[0], lerp_amount)
        y = utility.lerp(selected.pos[1], target.pos[1], lerp_amount)
        self.selection_pos = (x, y)

        if percent_time_complete >= 0.5 and self.is_due_event:
            self.is_travel_paused = True
            self.is_due_event = False
            self.events_triggered += 1
            self.game.change_scene(SceneType.EVENT)

        # check if at target pos
        elif percent_time_complete >= 1.0:
            # update flags
            self.selected_node = self.target_node
            self.target_node = None
            self.current_travel_time = 0
            self.selection_pos = self.selected_node.pos

            # trigger if not already completed
            if not self.selected_node.is_complete:
                #self._trigger_current_node()
                pass

            # update to allow input again
            self.game.overworld.state = OverworldState.READY

    def _trigger_current_node(self):
        """
        Activate the current node and trigger the scene change.
        """
        selected_node = self.selected_node
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

            node_type = self._get_random_node_type(False)
            scene = utility.node_type_to_scene_type(node_type)

        self.game.change_scene(scene)
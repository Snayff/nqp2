from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

import pygame
import pytweening

from scripts.core import utility
from scripts.core.base_classes.node_container import NodeContainer
from scripts.core.constants import DEFAULT_IMAGE_SIZE, Direction, SceneType
from scripts.scenes.overworld.elements.node2 import Node2

if TYPE_CHECKING:
    from scripts.core.game import Game
    from typing import List, Tuple, Dict, Optional

__all__ = ["Rings"]


class Rings(NodeContainer):
    def __init__(self, game: Game, centre: Tuple[int, int], outer_radius: float, num_rings: int):
        super().__init__(game)
        self.outer_radius: float = outer_radius
        self.centre: Tuple[int, int] = centre
        self.num_rings: int = num_rings

        self.rings: Dict[int, List[Node2]] = {}  # N.B. the key starts from 1
        self.selected_node: Optional[Node2] = None
        self.target_node: Optional[Node2] = None
        self.current_ring: int = 0
        self.selection_pos: Tuple[float, float] = (0, 0)  # where the selection is drawn

        self.max_travel_time: float = 0.5
        self.current_travel_time: float = 0.0
        self.is_travel_paused: bool = False
        self.is_due_event: bool = False  # true if waiting for an event to trigger
        self.events_triggered: int = 0  # number of events triggered so far

    def update(self, delta_time: float):
        for nodes in self.rings.values():
            for node in nodes:
                node.update(delta_time)

        # process change between nodes
        if self.target_node is not None and not self.is_travel_paused:
            self._transition_to_new_node(delta_time)

    def render(self, surface: pygame.surface):
        # DEBUG - draw centre
        pygame.draw.rect(surface, (255, 0, 0), ((self.centre[0] - 1, self.centre[1] - 1), (2, 2)))

        # draw selection

        node = self.selected_node
        radius = (node.icon.get_width() / 2) + 2
        pygame.draw.circle(surface, (255, 255, 255), self.selection_pos, radius)

        # draw the nodes on top of the ring
        gap_between_rings = self.outer_radius / self.num_rings
        for ring_count, ring in enumerate(self.rings.values()):
            # draw ring
            pygame.draw.circle(surface, (255, 255, 255), self.centre, gap_between_rings * (ring_count + 1), 1)
            # ring count + 1 as it starts at 0

            # draw nodes
            for node in ring:

                # draw connections
                if node.connected_outer_node is not None:
                    pygame.draw.line(surface, (255, 255, 255), node.pos, node.connected_outer_node.pos)

                node.render(surface)

    def generate_nodes(self):
        gap_between_rings = self.outer_radius / self.num_rings
        num_nodes = 4  # starting number of nodes

        # generate rings
        for ring_count in range(1, self.num_rings + 1):
            num_nodes += ring_count
            self.rings[ring_count] = []
            angle_between_nodes = 360 / num_nodes
            current_radius = gap_between_rings * ring_count

            # generate nodes for each ring
            for node_count in range(num_nodes):
                vec = pygame.math.Vector2(0, -current_radius).rotate(angle_between_nodes * node_count)
                x = self.centre[0] + vec.x - (DEFAULT_IMAGE_SIZE / 2)
                y = self.centre[1] + vec.y - (DEFAULT_IMAGE_SIZE / 2)

                # generate node type
                node_type = self._get_random_node_type()

                # get node icon
                node_icon = self._get_node_icon(node_type)

                # init node and save
                node = Node2(node_type, (x, y), node_icon)
                self.rings[ring_count].append(node)

        # generate connections between nodes
        num_connections = 2
        for ring_num, ring in self.rings.items():
            num_connections += ring_num

            # choose random nodes
            nodes_to_connect = self.game.rng.choices(ring, k=num_connections)
            for node in nodes_to_connect:

                # find nearest node in next ring
                try:
                    smallest_distance = 999
                    nearest_node = None
                    for outer_node in self.rings[ring_num + 1]:  # +1 for next outermost ring

                        # get distance between nodes
                        x2 = (node.pos[0] - outer_node.pos[0]) ** 2
                        y2 = (node.pos[1] - outer_node.pos[1]) ** 2
                        distance = math.sqrt(x2 + y2)

                        if distance < smallest_distance:
                            smallest_distance = distance
                            nearest_node = outer_node

                    # connect nodes
                    if nearest_node is not None:
                        node.connected_outer_node = nearest_node
                        nearest_node.connected_inner_node = node

                except KeyError:
                    pass

        # pick a random node in outer ring as starting position
        nodes = self.rings[len(self.rings)]
        node = self.game.rng.choice(nodes)
        self.selected_node = node
        self.selection_pos = node.pos

        # set current ring
        self.current_ring = len(self.rings)

    def select_next_node(self, direction: Direction):
        nodes = self.rings[self.current_ring]
        current_index = nodes.index(self.selected_node)

        # handle in ring movement
        if direction in (Direction.LEFT, Direction.RIGHT):
            # move clockwise
            if direction == Direction.LEFT:
                # handle index looping
                if current_index + 1 >= len(nodes):
                    current_index = 0
                else:
                    current_index += 1

            # move counter clockwise
            elif direction == Direction.RIGHT:
                # handle index looping
                if current_index - 1 < 0:
                    current_index = len(nodes) - 1
                else:
                    current_index -= 1

            # update selected node
            self.target_node = nodes[current_index]

        # handle cross ring movement
        elif direction in (Direction.UP, Direction.DOWN):
            # move inwards
            if direction == Direction.DOWN:
                # check for an inner connection
                if self.selected_node.connected_inner_node is not None:
                    self.target_node = self.selected_node.connected_inner_node
                    self.current_ring -= 1

            elif direction == Direction.UP:
                # check for an outer connection
                if self.selected_node.connected_outer_node is not None:
                    self.target_node = self.selected_node.connected_outer_node
                    self.current_ring += 1

    def roll_for_event(self):
        """
        Roll to see if an event will be triggered when transitioning between nodes.
        """
        # check if we have hit the limit of events
        if self.events_triggered >= self.game.data.config["overworld"]["max_events_per_level"]:
            return

        if self.game.rng.roll() < self.game.data.config["overworld"]["chance_of_event"]:
            self.is_due_event = True

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
            self.selected_node = self.target_node
            self.target_node = None
            self.current_travel_time = 0
            self.selection_pos = self.selected_node.pos


    def _trigger_current_node(self):
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

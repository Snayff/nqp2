from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.node_container import NodeContainer
from scripts.core.constants import Direction
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

        self.rings: Dict[int, List[Node2]] = {}
        self.selected_node: Optional[Node2] = None
        self.current_ring: int = 0

    def update(self, delta_time: float):
        for nodes in self.rings.values():
            for node in nodes:
                node.update(delta_time)

    def render(self, surface: pygame.surface):
        # DEBUG - draw centre
        pygame.draw.rect(surface, (255, 0, 0), ((self.centre[0] - 1, self.centre[1] - 1), (2, 2)))

        # draw selection
        if self.selected_node is not None:
            node = self.selected_node
            radius = (node.icon.get_width() / 2) + 2
            pygame.draw.circle(surface, (255, 255, 255), node.pos, radius)

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
                x = self.centre[0] + vec.x
                y = self.centre[1] + vec.y

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
            print(f"current_index: {current_index}")
            self.selected_node = nodes[current_index]

        # handle cross ring movement
        elif direction in (Direction.UP, Direction.DOWN):
            # move inwards
            if direction == Direction.DOWN:
                # check for an inner connection
                if self.selected_node.connected_inner_node is not None:
                    self.selected_node = self.selected_node.connected_inner_node
                    self.current_ring -= 1

            elif direction == Direction.UP:
                # check for an outer connection
                if self.selected_node.connected_outer_node is not None:
                    self.selected_node = self.selected_node.connected_outer_node
                    self.current_ring += 1


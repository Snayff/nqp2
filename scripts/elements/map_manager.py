from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.misc.constants import NodeState, NodeType

if TYPE_CHECKING:
    from scripts.management.game import Game
    from typing import List

__all__ = ["MapManager"]


class MapManager:
    """
    Manage the nodes on the map
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.nodes: List[Node] = []

    def update(self):
        for node in self.nodes:
            node.update()

    def render(self):
        for node in self.nodes:
            node.render()


class Node:
    """
    Represents a possible interaction on the map
    """

    def __init__(self):
        self.type: NodeType = NodeType.COMBAT
        self.state: NodeState = NodeState.REACHABLE

    def update(self):
        pass

    def render(self):
        pass

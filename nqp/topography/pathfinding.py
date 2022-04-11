from heapq import heappop, heappush, heappushpop
from typing import Any, List


class PriorityQueue:
    """
    PriorityQueue implementation using heapq

    """

    def __init__(self):
        self.elements: List[Any] = []
        self._pushback = None

    def __bool__(self) -> bool:
        if self._pushback is not None:
            return True
        return bool(self.elements)

    def put(self, item, priority: float):
        if self._pushback is not None:
            heappush(self.elements, self._pushback)
        self._pushback = priority, item

    def get(self):
        try:
            if self._pushback is None:
                return heappop(self.elements)[1]
            else:
                value = heappushpop(self.elements, self._pushback)[1]
                self._pushback = None
                return value
        except IndexError:
            raise IndexError("get from empty queue")


def search_terrain(terrain, start, end):
    """
    Perform basic a* search on a Terrain

    - return path from ``start`` to ``end``
    - ``start`` will not be included in the list
    - ``end`` will be the last item in the returned list
    - empty list will be returned if there is no path

    """
    queue = PriorityQueue()
    parent = dict()
    cost_so_far = dict()

    current = None
    parent[start] = None
    cost_so_far[start] = 0
    queue.put(start, 0)

    while queue:
        current = queue.get()

        if current == end:
            break

        for neighbor in terrain.get_exits(current):
            cost = cost_so_far[current] + terrain.cost(current, neighbor)
            if neighbor not in cost_so_far or cost < cost_so_far[neighbor]:
                parent[neighbor] = current
                cost_so_far[neighbor] = cost
                dist = abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1])
                queue.put(neighbor, cost + dist)

    path = [current]
    while parent.get(current, None) is not None:
        current = parent[current]
        path.append(current)
    path.pop()
    path.reverse()
    return path

import numpy

import tcod

my_map = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 1, 1, 1],
    [1, 1, 0, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 1, 1, 1],
    [1, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 1],
]
pathfinder = tcod.path.AStar(my_map)
my_path = pathfinder.get_path(0, 0, 5, 7)

for y, row in enumerate(my_map):
    print(''.join(['0' if (y, x) in my_path else (' ' if v else '#') for x, v in enumerate(row)]))

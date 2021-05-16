from typing import List


class Camera:
    def __init__(self):
        self.pos = [0, 0]

    def render_offset(self, pos: List = None):
        # handle mutable arg
        if pos is None:
            pos = [0, 0]

        # make a copy or conver to list if tuple
        pos = list(pos)

        pos[0] -= self.pos[0]
        pos[1] -= self.pos[1]
        return pos

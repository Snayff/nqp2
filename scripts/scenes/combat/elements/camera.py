from typing import TYPE_CHECKING
from typing import Dict, List

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union


class Camera:
    def __init__(self):
        self.pos = [0, 0]
        self.zoom = 1


    def render_offset(self, pos: List = None) -> List[int]:
        # handle mutable arg
        if pos is None:
            pos = [0, 0]

        # make a copy or conver to list if tuple
        pos = list(pos)

        pos[0] -= self.pos[0]
        pos[1] -= self.pos[1]
        return pos

    def bind(self, rect):
        self.pos[0] = max(rect.left, min(rect.right, self.pos[0]))
        self.pos[1] = max(rect.top, min(rect.bottom, self.pos[1]))

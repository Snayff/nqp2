from __future__ import annotations

import logging
from typing import List, Tuple, TYPE_CHECKING, Union

from pygame import Vector2

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = ["PointLike"]

PointLike = Union[Tuple[int, int], List[int], List[float], Vector2]

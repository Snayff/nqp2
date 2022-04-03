from __future__ import annotations

import logging

from typing import List, TYPE_CHECKING, Tuple, Union

from pygame import Vector2

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = ["PointLike"]

PointLike = Union[Tuple[int, int], List[int], List[float], Vector2]
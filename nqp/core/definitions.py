from __future__ import annotations

from typing import Tuple

from nqp.base_classes.ui_element import UIElement
from nqp.ui_elements.generic.ui_frame import UIFrame
from nqp.ui_elements.generic.ui_panel import UIPanel
from nqp.ui_elements.generic.ui_window import UIWindow
from nqp.ui_elements.tailored.unit_stats_window import UnitStatsWindow

__all__ = ["TileLocation", "UIElementLike", "UIContainerLike"]

TileLocation = Tuple[int, int]
UIElementLike = UIElement | UIFrame
UIContainerLike = UIPanel | UIWindow | UnitStatsWindow


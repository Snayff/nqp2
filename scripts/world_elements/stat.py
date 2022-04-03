from __future__ import annotations

import logging
from abc import ABC

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict, Any

__all__ = ["IntStat", "FloatStat"]


class Stat(ABC):
    """
    A container for an Entities Stat. If current_value is None then defaults to base_value.
    """
    def __init__(self, base_value, current_value=None):
        self._base_value = base_value
        if current_value is None:
            current_value = base_value
        self._current_value = current_value

    def reset(self):
        """
        Set value back to base value.
        """
        self._current_value = self._base_value

    @property
    def value(self):
        return self._current_value

    @value.setter
    def value(self, value):
        self._current_value = value

    def set_base_value(self, value):
        """
        Set the base or original value for the Stat.
        """
        self._base_value = value


class IntStat(Stat):
    def __init__(self, base_value: int, current_value: int = None):
        super().__init__(base_value, current_value)

    # methods readded to specify types

    @property
    def value(self) -> int:
        return self._current_value

    @value.setter
    def value(self, value: int):
        self._current_value = value

    def set_base_value(self, value: int):
        self._base_value = value


class FloatStat(Stat):
    def __init__(self, base_value: float, current_value: float = None):
        super().__init__(base_value, current_value)

    # methods readded to specify types

    @property
    def value(self) -> float:
        return self._current_value

    @value.setter
    def value(self, value: float):
        self._current_value = value

    def set_base_value(self, value: float):
        self._base_value = value


from __future__ import annotations

from typing import TYPE_CHECKING

from nqp.base_classes.stat import Stat

if TYPE_CHECKING:
    pass

__all__ = ["IntStat", "FloatStat"]


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

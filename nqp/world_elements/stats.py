from __future__ import annotations

from typing import TYPE_CHECKING

from nqp.base_classes.stat import Stat

if TYPE_CHECKING:
    pass

__all__ = ["IntStat", "FloatStat"]


class IntStat(Stat):
    def __init__(self, base_value: int):
        super().__init__(base_value)

    # methods readded to specify types

    @property
    def value(self) -> int:
        return super().value

    @property
    def base_value(self) -> int:
        return self._base_value

    @base_value.setter
    def base_value(self, value: int):
        self._base_value = value


class FloatStat(Stat):
    def __init__(self, base_value: float):
        super().__init__(base_value)

    # methods readded to specify types

    @property
    def value(self) -> float:
        return super().value

    @property
    def base_value(self) -> float:
        return self._base_value

    @base_value.setter
    def base_value(self, value: float):
        self._base_value = value

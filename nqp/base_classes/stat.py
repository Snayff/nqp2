from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Dict

__all__ = ["Stat"]


class Stat(ABC):
    """
    A container for an Entities Stat. If current_value is None then defaults to base_value.
    """

    def __init__(self, base_value):
        self.modifiers: Dict[Any:Callable] = dict()
        self._base_value = base_value

    def reset(self):
        """
        Set value back to base value.
        """
        self.modifiers.clear()

    @property
    def value(self):
        acc = 0
        for func in self.modifiers.values():
            acc += func(self._base_value)
        return self._base_value + acc

    def set_base_value(self, value):
        """
        Set the base or original value for the Stat.
        """
        self._base_value = value

    def apply_modifier(self, func: Callable, key: Any):
        """
        Add a modifier

        When value is calculated, ``func`` will be called with the base value

        Args:
            func: Any callable function
            key: Unique identifier for adding and removing

        """
        self.modifiers[key] = func

    def remove_modifier(self, key: Any):
        """
        Remove a modifier

        Args:
            key: Unique identifier for adding and removing

        """
        del self.modifiers[key]

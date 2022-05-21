from __future__ import annotations

import weakref
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

__all__ = ["UnitAttribute"]


class UnitAttribute(ABC):
    """
    A container for a Unit's Attribute

    # TODO - This is currently a copy of Stat and needs to be updated to work for bools only
        with False taking precedence over True

    """

    def __init__(self, base_value: bool):
        self._base_value: bool = base_value
        # weakkey dict will drop modifiers if they have been deleted
        self._modifiers = weakref.WeakKeyDictionary()
        self._override_value = None

    def reset(self):
        """
        Set value back to base value.
        """
        self._override_value = None
        self._modifiers.clear()

    @property
    def value(self):
        if self._override_value is not None:
            return self._override_value
        acc = 0
        for key, func in self._modifiers.items():
            acc += func(self._base_value)
        return self._base_value + acc

    @property
    def base_value(self):
        return self._base_value

    @base_value.setter
    def base_value(self, value):
        """
        Set the base or original value for the Stat.
        """
        self._base_value = value

    def override(self, value):
        """
        Force the value and ignore modifiers

        """
        self._override_value = value

    def apply_modifier(self, func: Callable, key: Any):
        """
        Add a modifier

        When value is calculated, ``func`` will be called with the base value

        Args:
            func: Any callable function
            key: Unique identifier for adding and removing

        """
        self._modifiers[key] = func

    def remove_modifier(self, key: Any):
        """
        Remove a modifier

        Args:
            key: Unique identifier for adding and removing

        """
        del self._modifiers[key]

    def has_modifier(self, key: Any):
        """
        Check if modifier is applied

        Args:
            key: Unique identifier for adding and removing

        """
        return key in self._modifiers

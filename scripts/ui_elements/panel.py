from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui_element import UIElement

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

__all__ = ["Panel"]


class Panel:
    """
    A container class for ui elements. Offers better support for selection management.
    """

    def __init__(self, elements: List, is_active: bool = False):

        self._elements: List = elements
        self._selected_index: int = 0
        self._is_active: bool = is_active

        self.set_active(is_active)

    def update(self, delta_time: float):
        for element in self._elements:
            element.update(delta_time)

    def draw(self, surface: pygame.Surface):
        for element in self._elements:
            element.draw(surface)

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def selected_element(self) -> UIElement:
        return self._elements[self.selected_index]

    @property
    def selected_index(self) -> int:
        return self._selected_index

    def set_selected_index(self, new_index: int):
        """
        Change selection to a given index.
        Note: Don't use within panel due to recursion issues.
        """
        self.unselect_all_elements()

        try:
            self._elements[new_index].is_selected = True
            self._selected_index = new_index
        except IndexError:
            logging.warning(
                f"Tried to select index {new_index} but it exceeds number of elements "
                f"{len(self._elements)}. Selected first element instead."
            )
            self.select_first_element()

    def set_active(self, is_active: bool):
        for element in self._elements:
            element.set_active(is_active)

    def set_selectable(self, is_selectable: bool):
        for element in self._elements:
            element.is_selectable = is_selectable

    def select_first_element(self):
        """
        Selects the first element and sets the rest to unselected.
        """
        self.unselect_all_elements()
        if len(self._elements) > 0:
            self._elements[0].is_selected = True
        else:
            logging.warning(f"Tried to select first element but no element to select in panel.")

    def unselect_all_elements(self):
        """
        Sets all elements is_selected to False and resets current_selected_index.
        """
        for element in self._elements:
            element.is_selected = False

        self._selected_index = 0

    def select_next_element(self):
        # unselect current
        self._elements[self.selected_index].is_selected = False

        starting_index = self.selected_index

        for index in range(len(self._elements)):

            # increment position
            self._selected_index += 1
            if self.selected_index > len(self._elements) - 1:
                self._selected_index = 0

            if self._elements[self.selected_index].is_selectable:
                # select
                self._elements[self.selected_index].is_selected = True

                if self.selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break

    def select_previous_element(self):
        # unselect current
        self._elements[self.selected_index].is_selected = False

        starting_index = self.selected_index

        for index in range(len(self._elements)):

            # increment position
            self._selected_index -= 1
            if self.selected_index < 0:
                self._selected_index = len(self._elements) - 1

            if self._elements[self.selected_index].is_selectable:
                # select
                self._elements[self.selected_index].is_selected = True

                if self.selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from typing import List, Tuple, Optional

__all__ = ["Panel"]


class Panel:
    """
    A container class for ui elements. Offers better support for selection management.
    """
    def __init__(self, elements: List, is_active: bool = False):

        self.elements: List = elements
        self.selected_index: int = 0
        self.is_active: bool = is_active

        self.set_active(is_active)


    def update(self, delta_time: float):
        for element in self.elements:
            element.update(delta_time)

    def set_active(self, is_active: bool):

        for element in self.elements:
            element.set_active(is_active)

    def render(self, surface: pygame.surface):
        for element in self.elements:
            element.render(surface)

    def select_first_element(self):
        """
        Selects the first element and sets the rest to unselected.
        """
        self.unselect_all_elements()
        self.elements[0].is_selected = True

    def unselect_all_elements(self):
        """
        Sets all elements is_selected to False and resets current_selected_index.
        """
        for element in self.elements:
            element.is_selected = False

        self.selected_index = 0

    def select_next_element(self):
        # unselect current
        self.elements[self.selected_index].is_selected = False

        starting_index = self.selected_index

        for index in range(len(self.elements)):

            # increment position
            self.selected_index += 1
            if self.selected_index > len(self.elements) - 1:
                self.selected_index = 0

            if self.elements[self.selected_index].is_selectable:
                # select
                self.elements[self.selected_index].is_selected = True

                if self.selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break

    def select_previous_element(self):
        # unselect current
        self.elements[self.selected_index].is_selected = False

        starting_index = self.selected_index

        for index in range(len(self.elements)):

            # increment position
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = len(self.elements) - 1

            if self.elements[self.selected_index].is_selectable:
                # select
                self.elements[self.selected_index].is_selected = True

                if self.selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break


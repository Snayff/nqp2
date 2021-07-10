from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
import self as self

from scripts.core.base_classes.ui_element import UIElement

if TYPE_CHECKING:
    from typing import List, Tuple, Optional

__all__ = []


class Panel:
    """
    A container class for ui elements.
    """
    def __init__(self, elements: List, is_active: bool = False):

        self.elements: List = elements
        self.current_selected_index: int = 0
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

    def unselect_all_elements(self):
        """
        Sets all elements is_selected to False and resets current_selected_index.
        """
        for element in self.elements:
            element.is_selected = False

        self.current_selected_index = 0

    def select_next_element(self):
        # unselect current
        self.elements[self.current_selected_index].is_selected = False

        starting_index = self.current_selected_index

        for index in range(len(self.elements)):

            # increment position
            self.current_selected_index += 1
            if self.current_selected_index > len(self.elements) - 1:
                self.current_selected_index = 0

            if self.elements[self.current_selected_index].is_selectable:
                # select
                self.elements[self.current_selected_index].is_selected = True

                if self.current_selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break

    def select_previous_element(self):
        # unselect current
        self.elements[self.current_selected_index].is_selected = False

        starting_index = self.current_selected_index

        for index in range(len(self.elements)):

            # increment position
            self.current_selected_index -= 1
            if self.current_selected_index < 0:
                self.current_selected_index = len(self.elements) - 1

            if self.elements[self.current_selected_index].is_selectable:
                # select
                self.elements[self.current_selected_index].is_selected = True

                if self.current_selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break


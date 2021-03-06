from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from nqp.base_classes.ui_element import UIElement

if TYPE_CHECKING:
    from typing import List, Union

    from nqp.core.definitions import UIElementLike
    from nqp.core.game import Game
    from nqp.ui_elements.generic.ui_tooltip import UITooltip

__all__ = ["UIPanel"]


class UIPanel:
    """
    A container class for UIElements. Offers support for selection management.
    Note that UIPanel doesnt have a position or size so one is inferred from it's contained
    elements.
    """

    def __init__(self, game: Game, elements: List[UIElementLike], is_active: bool = False):
        self._game: Game = game
        self._elements: List[UIElementLike] = elements
        self._selected_index: int = 0
        self._is_active: bool = is_active
        self._tooltip_ref: UITooltip | None = None  # Used to keep track of the tooltip in _elements

        self.set_active(is_active)

    def update(self, delta_time: float):
        for element in self._elements:
            element.update(delta_time)

        self._process_tooltip()

    def draw(self, surface: pygame.Surface):
        for element in self._elements:
            element.draw(surface)

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def selected_element(self) -> UIElement | None:
        for element in self._elements:
            if element.is_selected:
                return element
        # return self._elements[self.selected_index]
        return None

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
        Selects the first element and sets the rest to previously_selected.
        """
        self.unselect_all_elements()

        if len(self._elements) > 0:
            self._selected_index = -1
            self.select_next_element(False)

        else:
            logging.warning(f"Panel: Tried to select first element but no element to select in panel.")

    def unselect_all_elements(self):
        """
        Sets all elements is_selected to False and resets current_selected_index.
        """
        for element in self._elements:
            element.is_selected = False

        self._selected_index = 0
        self._clear_tooltip()

    def select_next_element(self, play_sound: bool = True):
        # unselect current
        self._elements[self.selected_index].is_selected = False
        self._clear_tooltip()

        starting_index = self.selected_index

        for index in range(len(self._elements)):

            # increment position
            self._selected_index += 1
            if self.selected_index > len(self._elements) - 1:
                self._selected_index = 0

            if self._elements[self.selected_index].is_selectable:
                # select
                self._elements[self.selected_index].is_selected = True

                if play_sound:
                    self._game.audio.play_sound("standard_click")

                if self.selected_index == starting_index:
                    logging.warning(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break

    def select_previous_element(self, play_sound: bool = True):
        # unselect current
        self._elements[self.selected_index].is_selected = False
        self._clear_tooltip()

        starting_index = self.selected_index

        for index in range(len(self._elements)):

            # increment position
            self._selected_index -= 1
            if self.selected_index < 0:
                self._selected_index = len(self._elements) - 1

            if self._elements[self.selected_index].is_selectable:
                # select
                self._elements[self.selected_index].is_selected = True

                if play_sound:
                    self._game.audio.play_sound("standard_click")

                if self.selected_index == starting_index:
                    logging.debug(f"Panel: Looped all the way back to the starting index. No others selectable.")

                break

    @property
    def width(self) -> int:
        width = 0
        for element in self._elements:
            if element.width > width:
                width = element.width
        return width

    @property
    def height(self) -> int:
        height = 0
        for element in self._elements:
            height += element.height
        return height

    @property
    def x(self) -> int:
        return self._elements[0].x

    @property
    def y(self) -> int:
        return self._elements[0].y

    def _process_tooltip(self):
        """
        Check if tooltip is needed and create or delete as required.
        """
        selected_element = self.selected_element

        if selected_element is None or not self.is_active:
            return

        if selected_element.show_tooltip and selected_element.tooltip_key is not None:
            if self._tooltip_ref is None:
                pos = pygame.Vector2(self.x + self.width + 1, self.y)
                from nqp.ui_elements.generic.ui_tooltip import UITooltip

                tooltip = UITooltip(self._game, pos, selected_element.tooltip_key)
                self._add_tooltip(tooltip)
        else:
            self._clear_tooltip()

    def _clear_tooltip(self):
        try:
            self._elements.remove(self._tooltip_ref)
            self._tooltip_ref = None
        except ValueError:
            # we dont care that it failed as it means there is no tooltip
            # but set to None just to be sure
            self._tooltip_ref = None

    def _add_tooltip(self, tooltip: UITooltip):
        self._tooltip_ref = tooltip
        self._elements.append(self._tooltip_ref)

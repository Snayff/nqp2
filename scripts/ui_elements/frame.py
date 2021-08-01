from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from scripts.core.base_classes.ui_element import UIElement
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import List, Optional, Tuple


__all__ = ["Frame"]


class Frame(UIElement):
    def __init__(
        self,
        pos: Tuple[int, int],
        image: Optional[pygame.surface] = None,
        text_and_font: Optional[Tuple[str, Font]] = (None, None),
        is_selectable: bool = False,
        max_line_width: int = 0,
    ):
        super().__init__(pos, is_selectable)

        self.image: Optional[pygame.surface] = image
        self.text: Optional[str] = str(text_and_font[0])
        self.font: Optional[Font] = text_and_font[1]
        self.line_width = max_line_width

        self._rebuild_surface()

    def update(self, delta_time: float):
        pass

    def _recalculate_size(self):
        width = 0
        height = 0

        if self.image:
            width += self.image.get_width()
            height += self.image.get_height()

        if self.text and self.font:
            width += self.font.width(self.text) + GAP_SIZE

            # N.B. doesnt amend height as is drawn next to image
            if height == 0:
                font_height = 12  # FIXME - get font height
                height += (font_height * self.font.calculate_number_of_lines(self.text, self.line_width))
        self.size = (width, height)
        self.surface = pygame.Surface(self.size, SRCALPHA)

    def _rebuild_surface(self):
        self._recalculate_size()

        surface = self.surface
        image = self.image
        text = self.text
        font = self.font

        if font:
            font_height = font.height
        else:
            font_height = 12

        # draw image
        if image:
            surface.blit(image, (0, 0))

        # draw text
        if text and font:
            if image:
                start_x = image.get_width() + GAP_SIZE
            else:
                start_x = 0

            font.render(text, surface, (start_x, font_height // 2), self.line_width)

    def set_text(self, text: str):
        self.text = str(text)

        self._rebuild_surface()

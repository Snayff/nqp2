from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui_element import UIElement
from scripts.core.constants import DEFAULT_IMAGE_SIZE, StatModifiedStatus
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import List, Tuple, Optional

    from scripts.core.game import Game


__all__ = ["Frame"]


class Frame(UIElement):
    def __init__(self, pos: Tuple[int, int], image: Optional[pygame.surface] = None,
            text_and_font: Optional[Tuple[str, Font]] = (None, None), is_selectable: bool = False):
        super().__init__(pos, is_selectable)

        self.image: Optional[pygame.surface] = image
        self.text: Optional[str] = str(text_and_font[0])
        self.font: Optional[Font] = text_and_font[1]

        self.rebuild_surface()

    def update(self, delta_time: float):
        pass

    def _recalculate_size(self):
        width = 0
        height = 0

        if self.image:
            width += self.image.get_width()
            height += self.image.get_height()

        if self.text and self.font:
            width += self.font.width(self.text)
            height += 12  # FIXME - get actual font height

        self.size = (width, height)
        self.surface = pygame.Surface(self.size)

    def rebuild_surface(self):
        self._recalculate_size()

        surface = self.surface
        image = self.image
        text = self.text
        font = self.font

        gap = 2
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
                start_x = image.get_width() + gap
            else:
                start_x = 0

            font.render(text, surface, (start_x, font_height // 2))



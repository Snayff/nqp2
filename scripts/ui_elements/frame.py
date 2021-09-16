from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from scripts.core.base_classes.ui_element import UIElement
from scripts.core.constants import DEFAULT_IMAGE_SIZE, GAP_SIZE
from scripts.core.utility import clamp
from scripts.ui_elements.fancy_font import FancyFont
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union


__all__ = ["Frame"]


class Frame(UIElement):
    def __init__(
        self,
        pos: Tuple[int, int],
        image: Optional[pygame.surface] = None,
        text_and_font: Optional[Tuple[str, Union[Font, FancyFont]]] = (None, None),
        is_selectable: bool = False,
        max_line_width: int = 0,
        max_height: Optional[int] = None,
    ):
        super().__init__(pos, is_selectable)

        self.image: Optional[pygame.surface] = image
        self.text: Optional[str] = str(text_and_font[0])
        self.font: Optional[Union[Font, FancyFont]] = text_and_font[1]
        self.line_width = max_line_width
        self.max_height = max_height

        self._rebuild_surface()

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.is_active:
            # FancyFont changes each frame so needs redrawing
            if isinstance(self.font, FancyFont):
                self.font.update(delta_time)

    def render(self, surface: pygame.Surface):
        super().render(surface)

        if self.is_active:
            # FancyFont changes each frame so needs redrawing
            if isinstance(self.font, FancyFont):
                self.font.render(surface)

    def _recalculate_size(self):
        image = self.image
        text = self.text
        font = self.font

        width = 0
        height = 0

        if image is not None:
            width += image.get_width()
            height += image.get_height()

        if text is not None and font is not None:
            width += font.width(self.text) + GAP_SIZE

            # N.B. doesnt amend height as is drawn next to image
            if height == 0:
                height += self.font.height

        # respect max height
        if self.max_height is not None:
            height_ = min(self.max_height, height)
        else:
            height_ = height

        self.size = (width, height_)
        self.surface = pygame.Surface(self.size, SRCALPHA)

    def _rebuild_surface(self):
        self._recalculate_size()

        surface = self.surface
        image = self.image
        text = self.text
        font = self.font

        # draw image
        if image:
            surface.blit(image, (0, 0))

        # draw text
        if text and font:
            if image:
                start_x = image.get_width() + GAP_SIZE
            else:
                start_x = 0

            font.render(text, surface, (start_x, font.line_height // 2), self.line_width)

    def set_text(self, text: str):
        self.text = str(text)

        self._rebuild_surface()

    def add_tier_background(self, tier: int):
        """
        Add a background to the frame, based on the tier given. Tiers can be 1-4.
        """
        tier_colours = {
            1: (141, 148, 150),
            2: (30, 117, 54),
            3: (30, 63, 117),
            4: (85, 30, 117),
        }

        # normalise value
        tier = clamp(tier, 1, 4)

        # create background and blit image onto it
        bg = pygame.Surface(self.image.get_size())
        bg.fill(tier_colours[tier])
        bg.blit(self.image, (0, 0))
        self.image = bg

        self._rebuild_surface()

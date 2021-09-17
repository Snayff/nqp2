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
        font: Optional[Union[Font, FancyFont]] = None,
        is_selectable: bool = False,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ):
        super().__init__(pos, is_selectable)

        self.image: Optional[pygame.surface] = image
        self.font: Optional[Union[Font, FancyFont]] = font
        self.max_width: Optional[int] = max_width
        self.max_height: Optional[int] = max_height

        self._override_font_attrs()
        self._recalculate_size()
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
        font = self.font

        width = 0
        height = 0

        if image is not None:
            width += image.get_width()
            height += image.get_height()

        if font is not None:
            width += font.width + GAP_SIZE

            # check which is taller, font or image
            if image is not None:
                height = max(image.get_height(), font.height)
            else:
                # no image so take font height
                height += font.height

        # respect max height
        if self.max_height is not None:
            height = min(height, self.max_height)

        # respect max width
        if self.max_width is not None:
            width = min(width, self.max_width)

        self.size = (width, height)

    def _rebuild_surface(self):
        self.surface = pygame.Surface(self.size, SRCALPHA)

        surface = self.surface
        image = self.image
        font = self.font

        # draw image
        if image:
            surface.blit(image, (0, 0))

        # draw text
        if font:
            # Font can be drawn once (FancyFont needs constant redrawing)
            if isinstance(font, Font):
                font.render(surface)

    def _override_font_attrs(self):
        """
        Force the font to use the frame's pos and max sizes.
        """
        image = self.image
        font = self.font

        if not font:
            return

        # offset for image, if there is one
        if image:
            image_width = image.get_width()
            x = image_width + GAP_SIZE
        else:
            image_width = 0
            x = 0

        # update font pos (remember, this is relative to the frame)
        y = font.line_height // 2
        font.pos = (x, y)

        # update font size
        if self.max_width is not None:
            new_line_width = max(self.max_width - image_width, font.line_width)
        else:
            self._recalculate_size()
            new_line_width = max(self.width - image_width, font.line_width)
        font.line_width = new_line_width

        # FancyFont needs to refresh
        if isinstance(font, FancyFont):
            font.refresh()
            pass

    def set_text(self, text: str):
        """
        Update the font text.
        """
        font = self.font

        text = str(text)

        if isinstance(font, FancyFont):
            font.raw_text = text
            font.refresh()

        elif isinstance(font, Font):
            font.text = text

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

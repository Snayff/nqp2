from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
from pygame import SRCALPHA

from nqp.base_classes.animation import Animation
from nqp.base_classes.image import Image
from nqp.base_classes.ui_element import UIElement
from nqp.core.constants import GAP_SIZE, TextRelativePosition
from nqp.core.utility import clamp
from nqp.ui_elements.generic.fancy_font import FancyFont
from nqp.ui_elements.generic.font import Font

if TYPE_CHECKING:
    from typing import Optional, Tuple, Union

    from nqp.core.game import Game

__all__ = ["UIFrame"]


class UIFrame(UIElement):
    """
    An extension of UIElement to offer more functionality within a helpful wrapper.
    """

    def __init__(
        self,
        game: Game,
        pos: pygame.Vector2,
        font: Optional[Union[Font, FancyFont]] = None,
        is_selectable: bool = False,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        image: Optional[Union[Image, Animation]] = None,
        text_relative_position: TextRelativePosition = None,
    ):
        super().__init__(game, pos, is_selectable)

        self._image: Optional[Union[Image, Animation]] = image
        self._font: Optional[Union[Font, FancyFont]] = font
        self._max_width: Optional[int] = max_width
        self._max_height: Optional[int] = max_height
        self._text_relative_position: Optional[TextRelativePosition] = text_relative_position

        self._override_font_attrs()
        self._recalculate_size()
        self.update(0)  # update to prevent the flash of all the text showing at the start
        self._rebuild_surface()

    def update(self, delta_time: float):
        if self.is_active:
            # FancyFont changes each frame so needs redrawing
            if isinstance(self._font, FancyFont):
                self._font.update(delta_time)

            # N.B. Animation is updates centrally so doesnt need to be updated here

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        is_dirty = False
        redraw_font = False

        if self.is_active:
            # FancyFont changes each frame so needs redrawing
            if isinstance(self._font, FancyFont):
                is_dirty = True
                redraw_font = True

            # Animation changes each frame
            if isinstance(self._image, Animation):
                is_dirty = True

            # rebuild surface first
            if is_dirty:
                self._rebuild_surface()

            if redraw_font:
                self._font.draw(self.surface)

    def _recalculate_size(self):
        image = self._image
        text_relative_position = self._text_relative_position
        font = self._font

        logging.info("Recalculating size for ui_frame.")

        width = image_width = 0
        height = image_height = 0

        if image is not None:
            image_width = image.surface.get_width()
            image_height = image.surface.get_height()

            width += image_width
            height += image_height

        logging.debug(f"Dimensions for image: ({image_width}, {image_height})")

        if font is not None:
            logging.debug(f"Dimensions for font: ({font.width}, {font.height})")

            if text_relative_position:
                if text_relative_position in (TextRelativePosition.ABOVE_IMAGE, TextRelativePosition.BELOW_IMAGE):
                    height += font.height + GAP_SIZE
                    width = max(font.width, image_width)
                else:
                    width += font.width + GAP_SIZE
            else:
                width += font.width + GAP_SIZE

                # check which is taller, font or image
                if image is not None:
                    height = max(image_height, font.height)
                else:
                    # no image so take font height
                    height += font.height

        logging.debug(f"Size of gap: {GAP_SIZE}")

        # respect max height
        if self._max_height is not None:
            height = min(height, self._max_height)

        # respect max width
        if self._max_width is not None:
            width = min(width, self._max_width)

        if text_relative_position:
            logging.debug(f"Recalculated size ({width}, {height}) for ui_frame with {text_relative_position.name}.")
        else:
            logging.debug(f"Recalculated size ({width}, {height}) for ui_frame with no text relative position")

        self.size = pygame.Vector2(width, height)

    def _rebuild_surface(self):
        self.surface = pygame.Surface(self.size, SRCALPHA)

        surface = self.surface
        image = self._image
        font = self._font
        text_relative_position = self._text_relative_position

        image_position: pygame.Vector2 = pygame.Vector2(0, 0)
        text_position: pygame.Vector2 = pygame.Vector2(0, 0)

        if text_relative_position is TextRelativePosition.ABOVE_IMAGE:
            image_position.y += font.height
        elif text_relative_position is TextRelativePosition.BELOW_IMAGE:
            text_position.y += image.height
        elif text_relative_position is TextRelativePosition.RIGHT_OF_IMAGE:
            text_position.x += image.height
        elif text_relative_position is TextRelativePosition.LEFT_OF_IMAGE:
            image_position.x += font.width

        # draw image
        if image is not None:
            surface.blit(image.surface, image_position)

        # draw text
        if font is not None:
            # Font can be drawn once (FancyFont needs constant redrawing so is handled in the draw method)
            if isinstance(font, Font):
                font.pos = text_position
                font.draw(surface)

    def _override_font_attrs(self):
        """
        Force the font to use the frame's pos and max sizes.
        """
        image = self._image
        font = self._font

        if not font:
            return

        # offset for image, if there is one
        if image:
            image_width = image.surface.get_width()
            x = image_width + GAP_SIZE
        else:
            image_width = 0
            x = 0

        # update font pos (remember, this is relative to the frame)
        y = font.line_height // 2
        font.pos = pygame.Vector2(x, y)

        # update font size
        if self._max_width is not None:
            new_line_width = max(self._max_width - image_width, font.line_width)
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
        font = self._font

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
        bg = pygame.Surface(self._image.surface.get_size())
        bg.fill(tier_colours[tier])
        bg.blit(self._image.surface, (0, 0))
        self._image = bg

        self._rebuild_surface()

    def pause_animation(self):
        """
        Pause the animation, if there is one
        """
        if isinstance(self._image, Animation):
            self._image.pause()

    def play_animation(self):
        """
        Play the animation, if there is one
        """
        if isinstance(self._image, Animation):
            self._image.play()

    def reset_animation(self):
        """
        Reset the animation, if there is one
        """
        if isinstance(self._image, Animation):
            self._image.reset()

    def stop_animation(self):
        """
        Stop the animation, if there is one
        """
        if isinstance(self._image, Animation):
            self._image.stop()

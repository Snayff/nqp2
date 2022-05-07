from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import WindowType, FontType
from nqp.core.definitions import UIContainerLike
from nqp.ui_elements.generic.ui_frame import UIFrame

from nqp.ui_elements.generic.ui_window import UIWindow

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from nqp.core.game import Game


__all__ = ["UITooltip"]


class UITooltip(UIWindow):
    """
    A UIWindow subclass for showing specific information about a hovered item.
    """

    def __init__(
            self,
            game: Game,
            pos: pygame.Vector2,
            tooltip_key: str,
    ):
        self.secondary_tooltips: None | UIWindow = None

        self._build_self(tooltip_key)

        super().__init__(game, WindowType.BASIC, pos, self.size, self._elements, True)

    def update(self, delta_time: float):
        super().update(delta_time)

    def draw(self, surface: pygame.Surface):
        self._draw_window(surface)
        super().draw(surface)

        if self.secondary_tooltips:
            self.secondary_tooltips.draw(surface)

    def _build_self(self, tooltip_key):
        """
        Get the content from data and build primary and secondary tooltips. Also recalcs size of self.
        """
        try:
            # build primary tooltip
            title = self._game.data.tooltips[tooltip_key]["title"]
            text = self._game.data.tooltips[tooltip_key]["text"]
            image_name = self._game.data.tooltips[tooltip_key]["image"]

        except KeyError:
            return

        text, keys = self._parse_text(text)
        frames = self._build_frames(title, text, image_name, self.pos)
        self._elements = self._elements + frames

        self._recalculate_size()

        # build secondary tooltips
        pos = pygame.Vector2(self.pos.x + self.width + 1, self.pos.y)  # +1 avoid overlap
        secondary_frames = []
        for key in keys:
            title = self._game.data.tooltips[key]["title"]
            text = self._game.data.tooltips[key]["text"]
            image_name = self._game.data.tooltips[key]["image"]
            text, keys = self._parse_text(text)
            frames = self._build_frames(title, text, image_name, pos)
            secondary_frames = secondary_frames + frames

            # increment pos
            last_frame = frames[-1]
            pos = pygame.Vector2(pos.x, last_frame.pos.y + last_frame.height + 1)  # +1 avoid overlap

        # add secondary frames to a window
        if secondary_frames:
            pos = pygame.Vector2(self.pos.x + self.width + 1, self.pos.y) # +1 avoid overlap
            height = 0
            width = secondary_frames[0].width
            for frame in secondary_frames:
                height += frame.height + 1
            self.secondary_tooltips = UIWindow(self._game, self._window_type, pos, pygame.Vector2(width, height),
                                               secondary_frames, True)

    @staticmethod
    def _parse_text(text: str) -> Tuple[str, List[str]]:
        """
        Return text without tags and a list of any keys for secondary tooltips.
        """
        # check for secondary tag
        start_indices = [i for i, char in enumerate(text) if char == "<"]
        end_indices = [i for i, char in enumerate(text) if char == ">"]
        secondary_tooltip_keys = []

        # confirm results are as expected
        if len(start_indices) != 0 and len(start_indices) == len(end_indices):

            # loop indices, remove tags and keep strings in tags for getting secondary tooltips
            for i, index in enumerate(start_indices):
                end = end_indices[i]
                secondary_tooltip_keys.append(text[index:end])

            # remove tags from text
            text = text.replace("<", "")
            text = text.replace(">", "")

        return text, secondary_tooltip_keys

    def _recalculate_size(self):
        """
        Recalculate the size of the tooltip based on the the elements.
        """
        height = 0
        width = self._elements[0].width
        for frame in self._elements:
            height += frame.height + 1  # account for overlap offset
        self.size = pygame.Vector2(width, height)

    def _build_frames(self, title: str, text: str, image_name: str, pos: pygame.Vector2) -> List[UIFrame]:
        """
        Build the various frames that make up the tooltip
        """
        frames = []
        font = self._game.visual.create_font(FontType.POSITIVE, title)
        frame = UIFrame(self._game, pos, font)
        frames.append(frame)

        font = self._game.visual.create_font(FontType.DEFAULT, text)
        pos = pygame.Vector2(pos.x, pos.y + frame.height + 1)  # +1 avoid overlap
        if image_name:
            image = self._game.visual.get_image(image_name)
            frame = UIFrame(self._game, pos, font, image=image)
        else:
            frame = UIFrame(self._game, pos, font)
        frames.append(frame)

        return frames

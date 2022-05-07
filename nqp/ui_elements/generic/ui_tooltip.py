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


class UITooltip(UIWindow):
    """
    A UIWindow subclass for showing specific information about a hovered item.
    """

    def __init__(
            self,
            game: Game,
            window_type: WindowType,
            pos: pygame.Vector2,
            tooltip_key: str,
    ):
        self.secondary_tooltips: None | UIWindow = None

        self._retrieve_content(tooltip_key)
        self._recalculate_size()

        super().__init__(game, window_type, pos, self.size, self._elements, True)

    def update(self, delta_time: float):
        super().update(delta_time)

    def draw(self, surface: pygame.Surface):
        self._draw_window(surface)
        super().draw(surface)

        if self.secondary_tooltips:
            self.secondary_tooltips.draw(surface)

    def _retrieve_content(self, tooltip_key):
        # build primary tooltip
        text = self._game.data.tooltips[tooltip_key]["text"]
        image_name = self._game.data.tooltips[tooltip_key]["image"]
        text, keys = self._parse_text(text)
        frame = self._build_frame(text, image_name, self.pos)
        self._elements.append(frame)

        # build secondary tooltips
        pos = pygame.Vector2(frame.pos.x + frame.width + 1, frame.pos.y)  # +1 for x offset
        secondary_frames = []
        for key in keys:
            text = self._game.data.tooltips[key]["text"]
            image_name = self._game.data.tooltips[key]["image"]
            text, keys = self._parse_text(text)
            frame = self._build_frame(text, image_name, pos)
            secondary_frames.append(frame)

            # increment pos
            pos = pygame.Vector2(pos.x, pos.y + frame.height + 1)  # +1 for y offset

        # add secondary frames to a window
        if secondary_frames:
            pos = pygame.Vector2(self.pos.x + frame.width, self.pos.y)
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
        Recalculate the size of the tooltip based on the first item in self._elements.
        """
        frame = self._elements[0]  # should only have 1, so grab first item
        self.size = pygame.Vector2(frame.width, frame.height)

    def _build_frame(self, text: str, image_name: str, pos: pygame.Vector2) -> UIFrame:
        font = self._game.visual.create_font(FontType.DEFAULT, text)
        if image_name:
            image = self._game.visual.get_image(image_name)
            frame = UIFrame(self._game, pos, font, image=image)
        else:
            frame = UIFrame(self._game, pos, font)

        return frame
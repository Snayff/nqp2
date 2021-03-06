from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import FontType, GAP_SIZE, WindowType
from nqp.ui_elements.generic.ui_frame import UIFrame
from nqp.ui_elements.generic.ui_window import UIWindow

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from nqp.core.definitions import UIContainerLike
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
        tooltip_key: str | None = None,
        tooltip_content: Tuple[str, str, str] | None = None,
    ):
        """
        Needs either tooltip_key or tooltip_content. tooltip_key takes precedent over
        tooltip_content, if both are provided only the key is used.
        """
        super().__init__(game, WindowType.BASIC, pos, pygame.Vector2(0, 0), [], True)

        self.secondary_tooltips: None | UIWindow = None
        self.max_width: int = 100

        # get the content from either param
        if tooltip_key is not None:
            content = self._get_content(tooltip_key)
            if content is not None:
                title, text, image_name = content
                self._build_self(title, text, image_name)
        elif tooltip_content is not None:
            title, text, image_name = tooltip_content
            self._build_self(title, text, image_name)

    def update(self, delta_time: float):
        super().update(delta_time)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        if self.secondary_tooltips:
            self.secondary_tooltips.draw(surface)

    def _get_content(self, tooltip_key: str) -> Tuple[str, str, str] | None:
        """
        Get the content from the tooltip data, using the key.
        Returns None if key not found.
        """
        try:
            title = self._game.data.tooltips[tooltip_key]["title"]
            text = self._game.data.tooltips[tooltip_key]["text"]
            image_name = self._game.data.tooltips[tooltip_key]["image"]

            return title, text, image_name

        except KeyError:
            return

    def _build_self(self, title: str, text: str, image_name: str):
        """
        Build primary and secondary tooltips.
        Also recalcs size of self and rebuilds the window surface to align to the new size.
        """
        text, keys = self._parse_text(text)
        pos = pygame.Vector2(self.pos.x + GAP_SIZE, self.pos.y + GAP_SIZE)
        frames = self._build_frames(title, text, image_name, pos)
        self._elements = self._elements + frames

        # need to recalc size and rebuild window to match
        self._recalculate_size()
        self._window_surface = self._build_window_surface()

        # build secondary tooltips
        pos = pygame.Vector2(self.pos.x + self.width + GAP_SIZE, self.pos.y + GAP_SIZE)
        secondary_frames = []
        for key in keys:
            title, text, image_name = self._get_content(key)
            text, keys = self._parse_text(text)
            frames = self._build_frames(title, text, image_name, pos)
            secondary_frames = secondary_frames + frames

            # increment pos
            last_frame = frames[-1]
            pos = pygame.Vector2(pos.x, last_frame.pos.y + last_frame.height + 1)  # +1 avoid overlap

        # add secondary frames to a window
        if secondary_frames:
            # recalc size
            height = 0
            width = 0
            for frame in secondary_frames:
                height += frame.height + 1
                if frame.width > width:
                    width = frame.width

            # add gap for whitespace
            width += GAP_SIZE
            height += GAP_SIZE * 2

            pos = pygame.Vector2(self.pos.x + self.width + 1, self.pos.y)  # +1 avoid overlap
            # create window, not tooltip, as we've already done all the work and we dont want recursive tooltips
            self.secondary_tooltips = UIWindow(
                self._game, self._window_type, pos, pygame.Vector2(width, height), secondary_frames, True
            )

    @staticmethod
    def _parse_text(text: str) -> Tuple[str, List[str]]:
        """
        Return text without tags and a list of any keys for secondary tooltips.
        """
        # check for secondary tags
        start_indices = [i for i, char in enumerate(text) if char == "<"]
        end_indices = [i for i, char in enumerate(text) if char == ">"]
        secondary_tooltip_keys = []

        # confirm results are as expected
        if len(start_indices) != 0 and len(start_indices) == len(end_indices):

            # loop indices, remove tags and keep strings in tags for getting secondary tooltips
            for i, index in enumerate(start_indices):
                end = end_indices[i]
                secondary_tooltip_keys.append(text[index + 1 : end])

            # remove tags from text
            text = text.replace("<", "")
            text = text.replace(">", "")

        return text, secondary_tooltip_keys

    def _recalculate_size(self):
        """
        Recalculate the size of the tooltip based on the the elements.
        """
        height = 0
        width = 0
        for frame in self._elements:
            height += frame.height + 1  # account for overlap offset

            # get biggest width
            if frame.width > width:
                width = frame.width

        # add gap for whitespace
        width += GAP_SIZE
        height += GAP_SIZE * 2

        self.size = pygame.Vector2(width, height)

    def _build_frames(self, title: str, text: str, image_name: str, pos: pygame.Vector2) -> List[UIFrame]:
        """
        Build the various frames that make up the tooltip
        """
        frames = []

        # title frame
        font = self._game.visual.create_font(FontType.POSITIVE, title)
        if image_name:
            image = self._game.visual.get_image(image_name)
            frame = UIFrame(self._game, pos, font, image=image)
        else:
            frame = UIFrame(self._game, pos, font)
        frames.append(frame)

        height = frame.height

        # content frame
        font = self._game.visual.create_font(FontType.DEFAULT, text)
        pos = pygame.Vector2(pos.x, pos.y + frame.height + 1)  # +1 avoid overlap
        frame = UIFrame(self._game, pos, font, max_width=self.max_width)
        frames.append(frame)

        height += frame.height

        return frames

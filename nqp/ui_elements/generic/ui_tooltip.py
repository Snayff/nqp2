from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import WindowType, FontType
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
        self._retrieve_content(tooltip_key)
        self._recalculate_size()

        super().__init__(game, window_type, pos, self.size, self._elements, True)


    def _retrieve_content(self, tooltip_key):
        text = self._game.data.tooltips[tooltip_key]["content"]
        image_name = self._game.data.tooltips[tooltip_key]["image"]
        text, keys = self._parse_text(text)

        # build frame
        font = self._game.visual.create_font(FontType.DEFAULT, text)
        if image_name:
            image = self._game.visual.get_image(image_name)
            frame = UIFrame(self._game, self.pos, font, image=image)
        else:
            frame = UIFrame(self._game, self.pos, font)
        self._elements.append(frame)

        # build additional frames
        if keys:
            pos = pygame.Vector2(frame.pos.x + frame.width + 1, frame.pos.y)  # +1 for x offset
            self._build_secondary_tooltips(keys, pos)

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
        pass

    def _build_secondary_tooltips(self, secondary_tooltip_keys: List[str], pos: pygame.Vector2):
        pass

#
# class UITooltip:
#
#     """
#     Tooltips will pop up after <rect_reference> has been hovered for <visible_delay> seconds and will show <text>.
#     They are bound by the display size and will adjust their placement automatically.
#     <rect_reference> should be a reference to a Rect that should be used to trigger the tooltip (likely the Rect
#     attribute of another UIElement).
#
#     Please note that Rects can be resized and moved without creating a new instance. This will be necessary when
#     binding to moving elements.
#     In the event that an element is in world space rather than an absolute space, the element should have an
#     alternative rect attribute that gets updated to the absolute rect position.
#     """
#
#     def __init__(self, game, text, font_id, rect_reference, width=200, padding=2, margin=2, alpha=100, visible_delay=1):
#         self._game = game
#         self.text = text
#         self.font_id = font_id
#         self.rect_reference = rect_reference
#         self.width = width
#         self.padding = padding
#         self.margin = margin
#         self.alpha = 100
#         self.cursor_height = 10
#         self.rect_hover_timer = 0
#         self.visible_delay = visible_delay
#         self.generate_text_surf()
#
#     def change_text(self, text):
#         self.text = text
#         self.generate_text_surf()
#
#     def generate_text_surf(self):
#         text_block = TextBlock(
#             self.text, self._game.visual.enhanced_fonts[self.font_id], max_width=self.width - self.padding * 2
#         )
#         self.text_surf = pygame.Surface(
#             (text_block.used_width + self.padding * 2, text_block.height + self.padding * 2)
#         )
#         self.text_surf.fill((0, 0, 2))
#         self.text_surf.set_colorkey((0, 0, 2))
#         text_block.draw(self.text_surf, (self.padding, self.padding))
#
#     def update(self, delta_time):
#         mouse_pos = self._game.input.mouse_pos
#         if self.rect_reference.collidepoint(mouse_pos):
#             self.rect_hover_timer += delta_time
#         else:
#             self.rect_hover_timer = 0
#
#     def draw(self, surf):
#         if self.rect_hover_timer >= self.visible_delay:
#             mouse_pos = self._game.input.mouse_pos
#             display_size = self._game.window.base_resolution
#
#             # prioritize placing the tooltip centered above the mouse
#             base_pos = [
#                 mouse_pos[0] - self.text_surf.get_width() // 2,
#                 mouse_pos[1] - self.text_surf.get_height() - self.margin,
#             ]
#
#             # correct position on X axis if showing off of the screen
#             base_pos[0] = max(base_pos[0], self.margin)
#             base_pos[0] = min(base_pos[0], display_size[0] - self.text_surf.get_width() - self.margin)
#
#             # show tooltip below mouse if it's clipping above the display
#             if base_pos[1] < self.margin:
#                 base_pos[1] = mouse_pos[1] + self.margin + self.cursor_height
#
#             # just draw an image instead if you don't want a rectangle background
#             bg_surf = pygame.Surface(self.text_surf.get_size())
#             bg_surf.set_alpha(self.alpha)
#
#             surf.blit(bg_surf, base_pos)
#             surf.blit(self.text_surf, base_pos)

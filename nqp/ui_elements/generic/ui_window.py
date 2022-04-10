from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from nqp.base_classes.image import Image
from nqp.core.constants import WindowType
from nqp.ui_elements.generic.ui_panel import UIPanel

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from nqp.core.game import Game

__all__ = ["UIWindow"]


class UIWindow(UIPanel):
    """
    A more feature rich UIPanel, containing its own visual style.
    """

    def __init__(
        self,
        game: Game,
        window_type: WindowType,
        pos: pygame.Vector2,
        size: pygame.Vector2,
        elements: List,
        is_active: bool = False,
    ):
        super().__init__(game, elements, is_active)
        self._images: Dict[str, Image] = self._load_window_images(window_type)
        self.pos: pygame.Vector2 = pos
        self.size: pygame.Vector2 = size

        self._window_surface: pygame.Surface = self._build_window_surface()

    def update(self, delta_time: float):
        super().update(delta_time)

    def draw(self, surface: pygame.Surface):
        self._draw_window(surface)
        super().draw(surface)

    def _load_window_images(self, window_type: WindowType) -> Dict[str, Image]:
        """
        Load the images for the given window type.
        """
        images = {}
        positions = [
            "bottom_left",
            "bottom_middle",
            "bottom_right",
            "centre",
            "left_middle",
            "right_middle",
            "top_left",
            "top_middle",
            "top_right",
        ]
        w_type = window_type.name.lower()

        # get all images
        for pos in positions:
            image_name = f"window_{w_type}_{pos}"
            image = self._game.visual.get_image(image_name)
            images[pos] = image

        return images

    def _draw_window(self, surface: pygame.Surface):
        """
        Draw the window images to create the visual border.
        """
        surface.blit(self._window_surface, self.pos)

    def _build_window_surface(self) -> pygame.Surface:
        """
        Build the 9 slice into a single surface
        """
        images = self._images
        window_width, window_height = self.size.x, self.size.y

        # create blank surface
        surface = pygame.Surface(self.size)

        # scale and draw centre
        centre = pygame.transform.smoothscale(images["centre"].surface, self.size)
        surface.blit(centre, (0, 0))

        # draw borders without corners
        y = 0
        for x in range(0, window_width, images["top_middle"].width):
            surface.blit(images["top_middle"].surface, (x, y))

        y = window_height - images["bottom_middle"].height
        for x in range(0, window_width, images["bottom_middle"].width):
            surface.blit(images["bottom_middle"].surface, (x, y))

        x = 0
        for y in range(0, window_height, images["left_middle"].height):
            surface.blit(images["left_middle"].surface, (x, y))

        x = window_width - images["right_middle"].width
        for y in range(0, window_height, images["right_middle"].height):
            surface.blit(images["right_middle"].surface, (x, y))

        # draw corners
        x = 0
        y = 0
        surface.blit(images["top_left"].surface, (x, y))

        x = 0
        y = window_height - images["bottom_left"].height
        surface.blit(images["bottom_left"].surface, (x, y))

        x = window_width - images["top_right"].width
        y = 0
        surface.blit(images["top_right"].surface, (x, y))

        x = window_width - images["bottom_right"].width
        y = window_height - images["bottom_right"].height
        surface.blit(images["bottom_right"].surface, (x, y))

        return surface

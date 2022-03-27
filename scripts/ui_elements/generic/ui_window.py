from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.image import Image
from scripts.core.constants import WindowType
from scripts.ui_elements.generic.ui_panel import UIPanel

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.core.game import Game

__all__ = ["UIWindow"]


class UIWindow:
    """
    A more feature rich container for UIElements, containing a panel and its own visual style.
    """
    def __init__(self, game: Game, window_type: WindowType):
        self._game: Game = game
        self._images: Dict[str, Image] = self._load_window_images(window_type)
        self.panel = UIPanel(self._game, [], True)

    def update(self, delta_time: float):
        self.panel.update(delta_time)

    def draw(self, surface: pygame.Surface):
        self._draw_window(surface)

        self.panel.draw(surface)

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
        w_type = window_type.name

        # get all images
        for pos in positions:
            image_name = f"window_{w_type}_{pos}"
            image = self._game.visuals.get_image(image_name)
            images[pos] = image

        return images

    def _draw_window(self, surface: pygame.Surface):
        """
        Draw the window images to create the visual border.
        """
        pass












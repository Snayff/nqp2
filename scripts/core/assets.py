from __future__ import annotations

import logging
from typing import List, TYPE_CHECKING

import pygame

from scripts.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, IMAGE_NOT_FOUND_PATH
from scripts.ui_elements.text import Font

if TYPE_CHECKING:
    from typing import Dict, Tuple

    from scripts.core.game import Game

__all__ = ["Assets"]


class Assets:
    def __init__(self, game: Game):
        self.game: Game = game

        self.fonts = {"small_red": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0))}

        # used to hold images called during runtime so only one copy ever exists.
        self.images: Dict[str, pygame.Surface] = {}

    def get_image(
        self,
        img_path: str,
        desired_dimensions: Tuple[int, int] = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE),
        copy: bool = False,
    ) -> pygame.Surface:
        """
        Get the specified image and resize if dimensions provided. Dimensions are in (width, height) format. If img
        path is "none" then a blank surface is created to the size of the desired dimensions, or TILE_SIZE if no
        dimensions provided.
        """
        # ensure numbers arent negative
        if desired_dimensions[0] <= 0 or desired_dimensions[1] <= 0:
            logging.warning(
                f"Get_image: Tried to use dimensions of {desired_dimensions}, which are negative. Default size "
                f"used instead."
            )
            desired_dimensions = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        # check if image path provided
        if str(img_path).lower() != "none":

            if f"{img_path}{desired_dimensions}" in self.images:
                image = self.images[f"{img_path}{desired_dimensions}"]
            else:
                try:
                    # try and get the image provided
                    image = pygame.image.load(str(ASSET_PATH / img_path)).convert_alpha()

                except Exception:
                    image = pygame.image.load(str(IMAGE_NOT_FOUND_PATH)).convert_alpha()
                    logging.warning(
                        f"Get_image: Tried to use {img_path} but it wasn`t found. Used the not_found image instead."
                    )
        else:
            image = pygame.Surface((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE))
            image.set_alpha(0)

        # resize if needed - should only need to resize if we havent got it from storage
        if image.get_width() != desired_dimensions[0] or image.get_height() != desired_dimensions[1]:
            width, height = desired_dimensions
            image = pygame.transform.smoothscale(image, (width, height))

            # add to storage
            self.images[f"{img_path}{desired_dimensions}"] = image

        # return a copy if requested
        if copy:
            return image.copy()
        else:
            return image

    def get_images(
        self, img_paths: List[str], desired_dimensions: Tuple[int, int], copy: bool = False
    ) -> List[pygame.Surface]:
        """
        Get a collection of images.
        """
        images = []

        for path in img_paths:
            images.append(self.get_image(path, desired_dimensions, copy))

        return images

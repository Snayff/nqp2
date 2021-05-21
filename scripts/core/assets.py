from __future__ import annotations

import logging
import os
from typing import List, TYPE_CHECKING

import pygame

from scripts.core.constants import ASSET_PATH, DATA_PATH, DEFAULT_IMAGE_SIZE, IMAGE_NOT_FOUND_PATH
from scripts.ui_elements.text import Font

if TYPE_CHECKING:
    from typing import Dict, Tuple

    from scripts.core.game import Game

__all__ = ["Assets"]


class Assets:
    def __init__(self, game: Game):
        self.game: Game = game

        self.fonts = {
            "warning": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0)),
            "disabled": Font(str(ASSET_PATH / "fonts/small_font.png"), (128, 128, 128)),
            "default": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 255, 255)),
        }

        # used to hold images so only one copy per dimension ever exists.
        self.images: Dict[str, Dict[str, pygame.Surface]] = self._load_images()


    def get_image(
        self,
        folder: str,
        image_name: str,
        desired_dimensions: Tuple[int, int] = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE),
        copy: bool = False,
    ) -> pygame.Surface:
        """
        Get the specified image and resize if dimensions provided. Dimensions are in (width, height) format. If img
        path is "none" then a blank surface is created to the size of the desired dimensions, or DEFAULT_IMAGE_SIZE
        if no dimensions provided.
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

    @staticmethod
    def _load_images() -> Dict[str, Dict[str, pygame.Surface]]:
        """
        Load all images by folder.
        """
        images = {}

        folders = [
            "nodes"
        ]

        for folder in folders:
            path = ASSET_PATH / folder
            images[folder] = {}
            for image_name in os.listdir(path):
                image = pygame.image.load(str(path / image_name)).convert_alpha()
                width = image.get_width()
                height = image.get_height()
                images[folder][f"{image_name.split('.')[0]}@{width}x{height}"] = image  # split to remove extension

        # add not found image to debug
        images["debug"] = {}
        image = pygame.image.load(str(ASSET_PATH / "debug/image_not_found.png")).convert_alpha()
        width = image.get_width()
        height = image.get_height()
        images["debug"][f"not_found@{width}x{height}"] = image
        # add transparent surface to debug
        image = pygame.Surface((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE))
        image.set_alpha(0)
        images["debug"][f"blank@{DEFAULT_IMAGE_SIZE}x{DEFAULT_IMAGE_SIZE}"] = image

        return images


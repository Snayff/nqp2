from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE
from scripts.ui_elements.text import Font

if TYPE_CHECKING:
    from typing import Dict, Tuple

    from scripts.core.game import Game

__all__ = ["Assets"]


class Assets:
    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self.game: Game = game

        self.fonts = {
            "warning": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0)),
            "disabled": Font(str(ASSET_PATH / "fonts/small_font.png"), (128, 128, 128)),
            "default": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 255, 255)),
        }

        # used to hold images so only one copy per dimension ever exists.
        self.images: Dict[str, Dict[str, pygame.Surface]] = self._load_images()

        # record duration
        end_time = time.time()
        logging.info(f"Assets: initialised in {format(end_time - start_time, '.2f')}s.")

    def get_image(
        self,
        folder_name: str,
        image_name: str,
        desired_dimensions: Tuple[int, int] = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE),
        copy: bool = False,
    ) -> pygame.Surface:
        """
        Get the specified image and resize if dimensions provided. Dimensions are in (width, height) format.

        A transparent surface can be returned by folder_name = "debug" and image_name = "blank".
        """
        desired_width, desired_height = desired_dimensions

        # ensure numbers arent negative
        if desired_width <= 0 or desired_height <= 0:
            logging.warning(
                f"Get_image: Tried to use dimensions of {desired_dimensions}, which are negative. Default size "
                f"used instead."
            )
            desired_dimensions = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        internal_name = f"{image_name}@{desired_width}x{desired_height}"

        # check if exists already
        try:
            image = self.images[folder_name][internal_name]

        except KeyError:
            # try and get the image specified
            try:
                image = pygame.image.load(str(ASSET_PATH / folder_name / image_name)).convert_alpha()

                # resize if needed - should only need to resize if we havent got it from storage
                if image.get_width() != desired_width or image.get_height() != desired_height:
                    image = pygame.transform.smoothscale(image, desired_dimensions)

                # add new image to storage
                self.images[folder_name][internal_name] = image

            except FileNotFoundError:
                # didnt find image requested so use not found image
                not_found_name = f"not_found@{desired_width}x{desired_height}"
                if not_found_name in self.images["debug"]:
                    image = self.images["debug"][not_found_name]
                else:
                    image = pygame.image.load(str(ASSET_PATH / "debug/image_not_found.png")).convert_alpha()

                    # add new image to storage
                    self.images["debug"][internal_name] = image

                logging.warning(
                    f"Get_image: Tried to use {folder_name}/{image_name} but it wasn't found. "
                    f"Used the not_found image instead."
                )

        # return a copy if requested
        if copy:
            return image.copy()
        else:
            return image

    @staticmethod
    def _load_images() -> Dict[str, Dict[str, pygame.Surface]]:
        """
        Load all images by folder.
        """
        images = {}

        # specify folders in assets that need to be loaded
        folders = ["nodes"]

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

        logging.info(f"Assets: All images loaded.")

        return images

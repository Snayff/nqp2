from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import pygame

from nqp.base_classes.resource_controller import ResourceController
from nqp.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, IMG_FORMATS

__all__ = ["ImageResourceController"]


class ImageResourceController(ResourceController):
    """
    Controls lazy loading for images
    """

    def __init__(self, image_folders: List[str]):
        """
        Initialize the super class without using weakref to avoid reloading images that don't
        always keep references in the Scene and would need to reload many times. It'd be better
        to use weakref but that would require images to be manually referenced at the Scene to
        keep them from having to reload.
        """
        ResourceController.__init__(self, loader=self._load_image, is_weakref=False)

        self._initialize_image_name_to_path_dict(image_folders)
        self._add_blank_surface_to_cache()

    def _initialize_image_name_to_path_dict(self, image_folders: List[str]) -> None:
        """
        Initialize a dictionary attribute mapping each image name to its path in disk
        :param image_folders: list of folders with image assets
        """

        # Convert string paths to Path objects
        image_folders_paths = [Path(ASSET_PATH / image_path) for image_path in image_folders]

        # Map each image name(without extension) to its file path
        name_to_path = {
            image_name.stem: image_path / image_name
            for image_path in image_folders_paths
            for image_name in image_path.iterdir()
            if image_name.suffix.lower()[1:] in IMG_FORMATS
        }

        # Include the path of the image used when an image is not found
        name_to_path["not_found"] = ASSET_PATH / "debug" / "image_not_found.png"

        self._image_name_to_path_dict = name_to_path

    def _add_blank_surface_to_cache(self) -> None:
        """
        Add the "blank" image to the cache with a blank alpha image
        """

        blank_size = DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE

        self._blank_surface = pygame.Surface(blank_size, pygame.SRCALPHA).convert_alpha()

        if self._blank_surface.get_size() != blank_size:
            self._blank_surface = pygame.transform.scale(self._blank_surface, blank_size)

        self.cache["blank"] = self._blank_surface

    def _load_image(self, item: str) -> pygame.Surface:
        """
        Load a new image from the passed item.

        :param item: a string specifying the image's name and resolution, formatted as file@WidthxHeight,
        such as town@640.0x360.0
        :return: a Surface with the loaded image.
        """
        # logging.info(f"Loading image '{item}'")

        # The image's name is before the at sign, width and height are after
        name, after_at_sign = item.split("@")

        """
        Width and height are strings formatted as floats so we get each string by splitting at "x",
        convert each to float then to int to later compare with the integer size of the surface
        """
        expected_size = list(map(int, map(float, after_at_sign.split("x"))))

        surface = pygame.image.load(self._image_name_to_path_dict[name]).convert_alpha()

        if surface.get_size() != expected_size:
            logging.debug(f"Image had to be rescaled from {surface.get_size()} to {expected_size}")
            surface = pygame.transform.scale(surface, expected_size)

        return surface

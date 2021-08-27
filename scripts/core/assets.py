from __future__ import annotations

import json
import logging
import os
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import Dict, Tuple

    from scripts.core.game import Game

__all__ = ["Assets"]


######### TO DO LIST  ##########
# TODO - either move functions to utility or make methods
# TODO - update get_image to be easier to use and support animations - use name, with optional action and frame?


def clip(surf, pos, size):
    x, y = pos
    x_size, y_size = size

    handle_surf = surf.copy()
    clip_r = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_r)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


def json_read(path):
    f = open(path, "r")
    data = json.load(f)
    f.close()
    return data


class Assets:
    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self.game: Game = game

        self.fonts = {
            "warning": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0)),
            "disabled": Font(str(ASSET_PATH / "fonts/small_font.png"), (128, 128, 128)),
            "default": Font(str(ASSET_PATH / "fonts/small_font.png"), (255, 255, 255)),
            "positive": Font(str(ASSET_PATH / "fonts/small_font.png"), (0, 255, 0)),
            "instruction": Font(str(ASSET_PATH / "fonts/small_font.png"), (240, 205, 48)),
            "notification": Font(str(ASSET_PATH / "fonts/large_font.png"), (117, 50, 168)),
        }

        # used to hold images so only one copy per dimension ever exists.
        self.images: Dict[str, Dict[str, pygame.Surface]] = self._load_images()

        # record duration
        end_time = time.time()
        logging.info(f"Assets: initialised in {format(end_time - start_time, '.2f')}s.")

        self.unit_animations = {
            unit: {
                action: self.load_image_dir(ASSET_PATH / "units/" / unit / action)
                for action in os.listdir(ASSET_PATH / "units/" / unit)
            }
            for unit in os.listdir(ASSET_PATH / "units/")
        }

        self.commander_animations = {
            commander: {
                action: self.load_image_dir(ASSET_PATH / "commanders/" / commander / action)
                for action in os.listdir(ASSET_PATH / "commanders/" / commander)
            }
            for commander in os.listdir(ASSET_PATH / "commanders/")
        }

        self.tilesets = {
            tileset.split(".")[0]: self.load_tileset(ASSET_PATH / "tiles" / tileset)
            for tileset in os.listdir(ASSET_PATH / "tiles")
        }

        self.maps = {map.split(".")[0]: json_read("data/maps/" + map) for map in os.listdir("data/maps")}

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
                image = pygame.image.load(str(ASSET_PATH / folder_name / image_name) + ".png").convert_alpha()

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

    def load_tileset(self, path):
        """
        Loads a tileset from a spritesheet.
        """

        tileset_data = []

        spritesheet = pygame.image.load(str(path)).convert_alpha()
        for y in range(spritesheet.get_height() // DEFAULT_IMAGE_SIZE):
            tileset_data.append([])
            for x in range(spritesheet.get_width() // DEFAULT_IMAGE_SIZE):
                tileset_data[-1].append(
                    clip(
                        spritesheet,
                        [x * DEFAULT_IMAGE_SIZE, y * DEFAULT_IMAGE_SIZE],
                        [DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE],
                    )
                )

        return tileset_data

    def load_image_dir(self, path, format="list"):
        """
        Load images in a directory with specified format.
        """

        images = None
        if format == "list":
            images = []
        if format == "dict":
            images = {}

        for img_path in os.listdir(path):
            img = pygame.image.load(str(path) + "/" + img_path).convert_alpha()
            if format == "list":
                images.append(img)
            if format == "dict":
                images[img_path.split(".")[0]] = img

        return images

    @staticmethod
    def _load_images() -> Dict[str, Dict[str, pygame.Surface]]:
        """
        Load all images by folder.

        N.B. if image isnt loading ensure the containing folder is listed in the method.
        """
        images = {}

        # specify folders in assets that need to be loaded
        folders = ["nodes", "stats", "ui", "buttons"]

        for folder in folders:
            path = ASSET_PATH / folder
            images[folder] = {}
            for image_name in os.listdir(path):
                if image_name.split(".")[-1] == "png":
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

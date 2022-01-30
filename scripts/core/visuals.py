from __future__ import annotations

import json
import logging
import os
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.animation import Animation
from scripts.core.base_classes.image import Image
from scripts.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, FontEffects, FontType
from scripts.core.utility import clamp, clip
from scripts.ui_elements.fancy_font import FancyFont
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

    from scripts.core.game import Game

__all__ = ["Visuals"]


class Visuals:
    """
    Store and manage images.
    """

    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        self._game: Game = game

        self._image_folders: List[str] = ["rooms", "stats", "ui", "buttons"]
        self._animation_folders: List[str] = []

        self._images: Dict[str, Dict[str, Image]] = {}  # folder_name: name, Image
        self._animations: Dict[str, Dict[str, Animation]] = {}  # folder_name: name, Animation
        self._fonts: Dict[FontType, Tuple[str, Tuple[int, int, int]]] = self._load_fonts()  # FontType: path, colour

        self._active_animations: List[Animation] = []

        # record duration
        end_time = time.time()
        logging.debug(f"Images: initialised in {format(end_time - start_time, '.2f')}s.")

    def update(self, delta_time: float):
        active_animations = self._active_animations

        # update animations
        for animation in active_animations:
            animation.update(delta_time)

            # remove the finished animations
            if animation.is_finished:
                self._active_animations.remove(animation)

    @staticmethod
    def _load_fonts():
        return {
            FontType.NEGATIVE: (str(ASSET_PATH / "fonts/small_font.png"), (255, 0, 0)),
            FontType.DISABLED: (str(ASSET_PATH / "fonts/small_font.png"), (128, 128, 128)),
            FontType.DEFAULT: (str(ASSET_PATH / "fonts/small_font.png"), (255, 255, 255)),
            FontType.POSITIVE: (str(ASSET_PATH / "fonts/small_font.png"), (0, 255, 0)),
            FontType.INSTRUCTION: (str(ASSET_PATH / "fonts/small_font.png"), (240, 205, 48)),
            FontType.NOTIFICATION: (str(ASSET_PATH / "fonts/large_font.png"), (117, 50, 168)),
        }

    def _load_images(self) -> Dict[str, Dict[str, Image]]:
        """
        Load all images by folder.
        """
        images = {}
        folders = self._image_folders

        # TODO - Images should be held in a dict with the top level folder as the key and then the image name as the
        #  nested key. e.g. {actions: {fireball: <Image>}} from /actions/fireball.png

        for folder in folders:
            path = ASSET_PATH / folder
            images[folder] = {}
            for image_name in os.listdir(path):
                if image_name.split(".")[-1] == "png":

                    # avoid duplicates
                    if image_name in images[folder].keys():
                        logging.warning(f"{image_name} already loaded, non-unique file name.")

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

    def _load_animations(self) -> Dict[str, Dict[str, Animation]]:
        """
        Load all images by folder.
        """
        images = {}
        folders = self._image_folders

        # TODO - Animations should be held in a dict with the top level folder as the key and then the name of each
        #  sub folder as a joined string for the animation name, to use as the nested key. The images in the final
        #  folder should be loaded into the Animation
        #  e.g. {bosses: {test_boss_move: <Animation>}} from /bosses/test_boss/move/*.png

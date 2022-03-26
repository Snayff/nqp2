from __future__ import annotations

import json
import logging
import os
import time
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.animation import Animation
from scripts.core.base_classes.image import Image
from scripts.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, FontEffects, FontType, IMG_FORMATS
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

        self._image_folders: List[str] = [
            "actions",
            "event_images",
            "factions",
            "items",
            "projectiles",
            "rooms",
            "stats",
            "tiles",
            "ui",
            "upgrades",
            "world",
        ]  # don't add debug folder
        self._animation_folders: List[str] = [
            "bosses",
            "commanders",
            "effects",
            "units",
            "ui_animations",
            "world_animations"
        ]

        self._images: Dict[str, pygame.Surface] = self._load_images()  # image_name: surface
        self._animation_frames: Dict[str, List[Image]] = self._load_animation_frames()
        # folder_name + "_" +  frame_name, [animation_frames]
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

    def _load_images(self) -> Dict[str, pygame.Surface]:
        """
        Load all images specified in self._image_folders
        """
        images = {}
        folders = self._image_folders

        for folder in folders:
            path = ASSET_PATH / folder
            for image_name in os.listdir(path):
                if image_name.split(".")[-1] in IMG_FORMATS:

                    # warn about duplicates
                    if image_name in images.keys():
                        logging.warning(f"{image_name} already loaded, non-unique file name.")

                    # load image
                    image = pygame.image.load(str(path / image_name)).convert_alpha()

                    # store image
                    width = image.get_width()
                    height = image.get_height()
                    images[f"{image_name.split('.')[0]}@{width}x{height}"] = image  # split to remove extension

        # add not found image
        image = pygame.image.load(str(ASSET_PATH / "debug/image_not_found.png")).convert_alpha()
        width = image.get_width()
        height = image.get_height()
        images[f"not_found@{width}x{height}"] = image

        # add transparent surface
        image = pygame.Surface((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE))
        image.set_alpha(0)
        images[f"blank@{DEFAULT_IMAGE_SIZE}x{DEFAULT_IMAGE_SIZE}"] = image

        return images

    def _load_animation_frames(self) -> Dict[str, List[Image]]:
        """
        Load all animation frames specified in self._animation_folders
        """
        animation_frames = {}
        folders = self._animation_folders

        # loop all specified folders
        for folder in folders:
            path = ASSET_PATH / folder

            directory_contents = os.listdir(path)
            for anim_folder_name in directory_contents:

                # we expect a sub folder for the item e.g. bosses/test_boss
                anim_path = path / anim_folder_name
                if os.path.isdir(anim_path):

                    # ...and then sub folders for each set of frames, e.g. bosses/test_boss/move
                    frame_folders = os.listdir(anim_path)
                    for frame_folder_name in frame_folders:
                        frame_folder_path = anim_path / frame_folder_name
                        if os.path.isdir(frame_folder_path):

                            # load the frames
                            animation_frames_folder = os.listdir(frame_folder_path)
                            for frame_name in animation_frames_folder:
                                if frame_name.split(".")[-1] in IMG_FORMATS:

                                    # warn about duplicates
                                    if frame_name in animation_frames.keys():
                                        logging.warning(
                                            f"Animation [{frame_name}] already loaded; non-unique file " f"name."
                                        )

                                    frame_path = path / anim_folder_name / frame_folder_name / frame_name
                                    image = pygame.image.load(str(frame_path)).convert_alpha()
                                    image_ = Image(image=image)

                                    # record the frame
                                    try:
                                        animation_frames[anim_folder_name + "_" + frame_folder_name].append(image_)
                                    except KeyError:
                                        animation_frames[anim_folder_name + "_" + frame_folder_name] = [image_]

        return animation_frames

    def create_animation(self, animation_name: str, frame_name: str, loop: bool = True) -> Animation:
        """
        Create a new animation and add it to the internal update list.
        """
        frames = self._animation_frames[animation_name + "_" + frame_name]
        anim = Animation(frames, loop=loop)
        self._active_animations.append(anim)
        return anim

    def get_image(
        self,
        image_name: str,
        size: Tuple[int, int] = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE),
        copy: bool = False,
    ) -> Image:
        """
        Get an image from the library.
        If a size is specified and it differs to the size held then the image is resized before returning.
        If copy = True then a copy of the image held in the library is provided. Remember to use a copy if you want
        to amend the image, otherwise the copy in the library is amended.

        A transparent surface is available with the name "blank".
        """

        # normalise size
        desired_width, desired_height = size

        # ensure numbers arent negative
        if desired_width <= 0 or desired_height <= 0:
            logging.warning(
                f"Get_image: Tried to use dimensions of {size}, which are negative. Default size " f"used instead."
            )
            size = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)

        internal_name = f"{image_name}@{desired_width}x{desired_height}"

        # check if exists already
        try:
            image = self._images[internal_name]

        except KeyError:
            image = None
            for held_image_name in self._images.keys():
                if image_name in held_image_name:
                    image = self._images[held_image_name]
                    break

            # if no image found replace with not found
            if image is None:
                logging.warning(f"Image requested [{image_name}] not found.")
                image_ = self.get_image("not_found")
                image = image_.surface
            else:
                # resize and store resized image
                assert isinstance(image, pygame.Surface)
                image = pygame.transform.smoothscale(image.copy(), size)

                self._images[f"not_found@{desired_width}x{desired_height}"] = image

        # return a copy if requested
        if copy:
            final_image = Image(image=image.copy())
        else:
            final_image = Image(image=image)

        return final_image

    def create_font(self, font_type: FontType, text: str, pos: Tuple[int, int] = (0, 0), line_width: int = 0) -> Font:
        """
        Create a font instance.
        """
        line_width = clamp(line_width, 0, self._game.window.width)
        path, colour = self._fonts[font_type]
        font = Font(path, colour, text, line_width, pos)
        return font

    def create_fancy_font(
        self,
        text: str,
        pos: Tuple[int, int] = (0, 0),
        line_width: int = 0,
        font_effects: Optional[List[FontEffects]] = None,
    ) -> FancyFont:
        """
        Create a FancyFont instance. If line_width isnt given then will default to full screen.
        """
        line_width = clamp(line_width, 0, self._game.window.width)

        # handle mutable default
        if font_effects is None:
            font_effects = []

        font = FancyFont(text, pos, line_width, font_effects)
        return font

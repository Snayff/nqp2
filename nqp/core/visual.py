from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pygame

from nqp.base_classes.animation import Animation
from nqp.base_classes.image import Image
from nqp.core.constants import ASSET_PATH, DEFAULT_IMAGE_SIZE, FontEffects, FontType, IMG_FORMATS
from nqp.core.debug import Timer
from nqp.core.utility import clamp, clip
from nqp.resource_controllers.image_resource_controller import ImageResourceController
from nqp.ui_elements.generic.fancy_font import FancyFont
from nqp.ui_elements.generic.font import Font

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

    from nqp.core.game import Game

__all__ = ["Visual"]


class Visual:
    """
    Store and manage images.
    """

    def __init__(self, game: Game):
        with Timer("Visual: initialised"):

            self._game: Game = game

            self._image_folders: List[str] = [  # must be the folder that contains the images
                "actions",
                "event_images",
                "factions",
                "items",
                "projectiles",
                "rooms",
                "tiles",
                "ui/backgrounds",
                "ui/borders",
                "ui/cursors",
                "ui/icons",
                "ui/keys",
                "ui/records",
                "ui/resources",
                "ui/stats",
                "ui/windows/basic",
                "ui/windows/fancy",
                "upgrades",
                "world",
            ]  # don't add debug folder
            self._animation_folders: List[str] = [  # must be the folder that contains the folders of images
                "bosses",
                "commanders",
                "effects",
                "units",
                "ui_animations",
                "world_animations",
            ]

            self.tilesets = {  # TODO - refactor to align to style
                tileset.split(".")[0]: self._load_tileset(ASSET_PATH / "tiles" / tileset)
                for tileset in os.listdir(ASSET_PATH / "tiles")
            }

            self._images: ImageResourceController = ImageResourceController(self._image_folders)
            self._animation_frames: Dict[str, Dict[str, List[Image]]] = self._load_animation_frames()
            # folder_name: {frame_name, [animation_frames]}
            self._fonts: Dict[FontType, Tuple[str, Tuple[int, int, int]]] = self._load_fonts()  # FontType: path, colour

            self._active_animations: List[Animation] = []

    def update(self, delta_time: float):
        active_animations = self._active_animations

        # update animations
        mod_delta = delta_time
        for animation in active_animations:
            animation.update(mod_delta, self._game.memory.game_speed)

            # remove the finished animations
            if animation.is_finished and animation.delete_on_finish:
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

    def _load_animation_frames(self) -> Dict[str, Dict[str, List[Image]]]:
        """
        Load all animation frames specified in self._animation_folders
        """
        animations = {}
        folders = self._animation_folders
        anim_counter = 0
        frame_set_counter = 0
        frame_counter = 0

        # loop all specified folders
        for folder in folders:
            path = ASSET_PATH / folder

            directory_contents = os.listdir(path)
            for anim_folder_name in directory_contents:
                # check we have data for the given animation
                try:
                    if anim_folder_name not in getattr(self._game.data, folder):
                        continue
                except AttributeError:
                    # we didnt find the folder in Data, so carry on regardless
                    pass

                # we expect a sub folder for the item e.g. bosses/test_boss
                anim_path = path / anim_folder_name
                if os.path.isdir(anim_path):
                    animations[anim_folder_name] = {}
                    anim_counter += 1

                    # ...and then sub folders for each set of frames, e.g. bosses/test_boss/move
                    frame_sets = os.listdir(anim_path)
                    for frame_set_name in frame_sets:

                        # warn about duplicates
                        if frame_set_name in animations[anim_folder_name].keys():
                            logging.warning(
                                f"Animation's frame set [{frame_set_name}] already loaded; non-unique file name."
                            )

                        frame_set_path = anim_path / frame_set_name
                        if os.path.isdir(frame_set_path):
                            animations[anim_folder_name][frame_set_name] = []
                            frame_set_counter += 1

                            # load the frames
                            animation_frames_folder = os.listdir(frame_set_path)
                            for frame_name in animation_frames_folder:
                                if frame_name.split(".")[-1] in IMG_FORMATS:

                                    frame_path = path / anim_folder_name / frame_set_name / frame_name
                                    image = pygame.image.load(str(frame_path)).convert_alpha()
                                    image_ = Image(image=image)

                                    # record the frame
                                    animations[anim_folder_name][frame_set_name].append(image_)

                                    frame_counter += 1

        logging.debug(
            f"Visual: {anim_counter} Animations loaded, containing {frame_set_counter} frame sets, "
            f"made up of {frame_counter} frames."
        )

        return animations

    def _load_tileset(self, path):
        """
        Loads a tileset from a spritesheet.
        """
        # TODO - rewrite to align to other load styles

        tileset_data = []

        spritesheet = pygame.image.load(str(path)).convert_alpha()
        for y in range(spritesheet.get_height() // DEFAULT_IMAGE_SIZE):
            tileset_data.append([])
            for x in range(spritesheet.get_width() // DEFAULT_IMAGE_SIZE):
                tileset_data[-1].append(
                    clip(
                        spritesheet,
                        x * DEFAULT_IMAGE_SIZE,
                        y * DEFAULT_IMAGE_SIZE,
                        DEFAULT_IMAGE_SIZE,
                        DEFAULT_IMAGE_SIZE,
                    )
                )

        return tileset_data

    def create_animation(
        self, animation_name: str, frame_set_name: str, loop: bool = True, uses_simulation_time: bool = True
    ) -> Animation:
        """
        Create a new animation and add it to the internal update list.
        """
        frames = self._animation_frames[animation_name]
        anim = Animation(
            frames, loop=loop, starting_frame_set_name=frame_set_name, uses_simulation_time=uses_simulation_time
        )
        self._active_animations.append(anim)
        return anim

    def get_image(
        self,
        image_name: str,
        size: pygame.Vector2 = (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE),
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

    def create_font(
        self, font_type: FontType, text: str, pos: pygame.Vector2 = pygame.Vector2(0, 0), line_width: int = 0
    ) -> Font:
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
        pos: pygame.Vector2 = (0, 0),
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

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, TypeVar

import pygame

from nqp.core.constants import IMG_FORMATS, SceneType

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

_V = TypeVar("_V", int, float)  # to represent where we don't know which type is being used

__all__ = [
    "swap_colour",
    "clip",
    "offset",
    "lerp",
    "clamp",
    "itr",
    "scene_to_scene_type",
    "next_number_in_loop",
    "grid_up",
    "grid_right",
    "grid_down",
    "grid_left",
    "distance_to",
    "angle_to",
    "get_direction",
    "percent_to_float",
]


def swap_colour(img, old_c, new_c):
    img.set_colorkey(old_c)
    surface = img.copy()
    surface.fill(new_c)
    surface.blit(img, (0, 0))
    surface.set_colorkey((0, 0, 0))
    return surface


def clip(surface, x, y, x_size, y_size) -> pygame.Surface:
    """
    Clip a subsurface from a surface.
    """
    handle_surf = surface.copy()
    clip_r = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_r)
    image = surface.subsurface(handle_surf.get_clip())
    return image.copy()


def offset(list_: List, offset_, offset_mult=1):
    for i, val in enumerate(list_):
        list_[i] += offset_[i] * offset_mult

    return list_


def lerp(initial_value: float, target_value: float, lerp_fraction: float) -> float:
    """
    Linear interpolation between initial and target by amount. Fraction clamped between 0 and 1. >=0.99 is treated
    as 1 to handle float imprecision.
    """
    clamped_lerp_fraction = clamp(lerp_fraction, 0, 1)

    if clamped_lerp_fraction >= 0.99:
        return target_value
    else:
        return initial_value * (1 - clamped_lerp_fraction) + target_value * clamped_lerp_fraction


def clamp(value: _V, min_value: _V, max_value: _V) -> _V:
    """
    Return the value, clamped between min and max.
    """
    return max(min_value, min(value, max_value))


def itr(iterable):
    """
    An iteration tool for easy removal.
    """
    return sorted(enumerate(iterable), reverse=True)


def scene_to_scene_type(scene) -> SceneType:
    """
    Take a Scene and return the relevant SceneType
    """
    from nqp.scenes.gallery.scene import GalleryScene
    from nqp.scenes.main_menu.scene import MainMenuScene
    from nqp.scenes.run_setup.scene import RunSetupScene
    from nqp.scenes.unit_data.scene import UnitDataScene
    from nqp.scenes.view_troupe.scene import ViewTroupeScene

    if type(scene) is ViewTroupeScene:
        scene = SceneType.VIEW_TROUPE
    elif type(scene) is RunSetupScene:
        scene = SceneType.RUN_SETUP
    elif type(scene) is UnitDataScene:
        scene = SceneType.DEV_DATA_EDITOR
    elif type(scene) is MainMenuScene:
        scene = SceneType.MAIN_MENU
    elif type(scene) is GalleryScene:
        scene = SceneType.DEV_GALLERY
    else:
        logging.error(f"scene_to_scene_type: Scene ({scene}) not found.")

    return scene


def next_number_in_loop(start: int, loop_size: int) -> int:
    if start + 1 >= loop_size:
        result = 0
    else:
        result = start + 1

    return result


def previous_number_in_loop(start: int, loop_size: int) -> int:
    """
    If at max loop size, returns loop size -1.
    """
    if start - 1 < 0:
        result = loop_size - 1
    else:
        result = start - 1

    return result


def grid_up(selected: int, width: int, height: int):
    return selected - width


def grid_down(selected: int, width: int, height: int):
    index = selected + width
    length = width * height
    if index >= length:
        index -= length
    return index


def grid_left(selected: int, width: int, height: int):
    if selected % width == 0:
        index = selected + width - 1
    else:
        index = selected - 1
    return index


def grid_right(selected: int, width: int, height: int):
    index = selected + 1
    length = width * height
    if index % width == 0 or index >= length:
        index -= width
    return index


def distance_to(start_pos: pygame.Vector2, end_pos: pygame.Vector2) -> float:
    """
    Find the distance to another position.
    """
    return math.sqrt((start_pos[0] - end_pos[0]) ** 2 + (start_pos[1] - end_pos[1]) ** 2)


def angle_to(start_pos: pygame.Vector2, end_pos: pygame.Vector2) -> float:
    """
    Find the angle to another position.
    """
    return math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])


def get_direction(angle: float, move_distance: float) -> pygame.Vector2:
    """
    Find the direction based on the angle and distance
    """
    return pygame.Vector2(math.cos(angle) * move_distance, math.sin(angle) * move_distance)


def percent_to_float(percent_string: str):
    """
    Convert string representation of percent into a float
    """
    return float(percent_string.strip("%")) / 100.0

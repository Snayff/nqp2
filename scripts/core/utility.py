from __future__ import annotations

import logging
from typing import List, TypeVar

import pygame

from scripts.core.constants import NodeType, SceneType

_V = TypeVar("_V", int, float)  # to represent where we don't know which type is being used

__all__ = ["swap_color", "clip", "offset", "lerp", "clamp", "itr", "scene_to_scene_type"]


def swap_color(img, old_c, new_c):
    img.set_colorkey(old_c)
    surface = img.copy()
    surface.fill(new_c)
    surface.blit(img, (0, 0))
    surface.set_colorkey((0, 0, 0))
    return surface


def clip(surface, x, y, x_size, y_size):
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
    from scripts.scenes.combat.scene import CombatScene
    from scripts.scenes.event.scene import EventScene
    from scripts.scenes.gallery.scene import GalleryScene
    from scripts.scenes.inn.scene import InnScene
    from scripts.scenes.main_menu.scene import MainMenuScene
    from scripts.scenes.overworld.scene import OverworldScene
    from scripts.scenes.post_combat.scene import PostCombatScene
    from scripts.scenes.run_setup.scene import RunSetupScene
    from scripts.scenes.training.scene import TrainingScene
    from scripts.scenes.unit_data.scene import UnitDataScene
    from scripts.scenes.view_troupe.scene import ViewTroupeScene

    if type(scene) is CombatScene:
        scene = SceneType.COMBAT
    elif type(scene) is ViewTroupeScene:
        scene = SceneType.VIEW_TROUPE
    elif type(scene) is TrainingScene:
        scene = SceneType.TRAINING
    elif type(scene) is InnScene:
        scene = SceneType.INN
    elif type(scene) is OverworldScene:
        scene = SceneType.OVERWORLD
    elif type(scene) is EventScene:
        scene = SceneType.EVENT
    elif type(scene) is PostCombatScene:
        scene = SceneType.REWARD
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


def node_type_to_scene_type(node_type: NodeType) -> SceneType:
    if node_type == NodeType.COMBAT:
        scene = SceneType.COMBAT
    elif node_type == NodeType.INN:
        scene = SceneType.INN
    elif node_type == NodeType.TRAINING:
        scene = SceneType.TRAINING
    elif node_type == NodeType.EVENT:
        scene = SceneType.EVENT
    elif node_type == NodeType.BLANK:
        scene = SceneType.OVERWORLD

    else:
        logging.error(f"node_type_to_scene_type: Node type ({node_type} not found. Default to Combat.")
        scene = SceneType.COMBAT

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
